#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import csv
import calendar
from datetime import datetime, timedelta

# =============================
# CONSTANTES / ENDPOINTS
# =============================
API_BASE = "https://api.sse.cisco.com"
AUTH_URL = f"{API_BASE}/auth/v2/token"
ACTIVITY_ENDPOINT = f"{API_BASE}/reports/v2/activity"

# =============================
# UTILITÁRIOS DE TEMPO
# =============================
def dt_to_epoch_millis(dt: datetime) -> int:
    """
    Converte datetime NAIVE (interpretado como hora local) para epoch em milissegundos.
    Mantém o comportamento que funcionava antes (equivalente a time.mktime).
    """
    return int(time.mktime(dt.timetuple()) * 1000)

def fmt_dt(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def elapsed(start_ts: float) -> str:
    return str(timedelta(seconds=int(time.time() - start_ts)))

# =============================
# RATE LIMITER (MÁX 5000/HORA)
# =============================
class RateLimiter:
    def __init__(self, max_requests=5000, per_seconds=3600):
        self.max_requests = max_requests
        self.per_seconds = per_seconds
        self.window_start = time.time()
        self.count = 0

    def check(self):
        now = time.time()
        # reset da janela se passou 1h
        if now - self.window_start >= self.per_seconds:
            self.window_start = now
            self.count = 0

        if self.count >= self.max_requests:
            wait = int(self.per_seconds - (now - self.window_start))
            if wait < 0:
                wait = 0
            print(f"\n⏸️ Rate limit atingido ({self.max_requests}/hora). Aguardando {wait}s...")
            time.sleep(wait)
            self.window_start = time.time()
            self.count = 0

        self.count += 1

# =============================
# AUTENTICAÇÃO
# =============================
def get_token(client_id: str, client_secret: str) -> str:
    resp = requests.post(
        AUTH_URL,
        data={"grant_type": "client_credentials"},
        auth=(client_id, client_secret),
        timeout=30
    )
    resp.raise_for_status()
    return resp.json()["access_token"]

def prompt_credentials_with_test() -> tuple[str, str, str]:
    """
    Pede CLIENT_ID/CLIENT_SECRET até conseguir um token válido.
    Retorna (client_id, client_secret, token).
    """
    while True:
        client_id = input("🔑 CLIENT_ID: ").strip()
        client_secret = input("🔑 CLIENT_SECRET: ").strip()
        try:
            token = get_token(client_id, client_secret)
            print("✅ Autenticação OK.\n")
            return client_id, client_secret, token
        except requests.HTTPError as e:
            msg = ""
            try:
                msg = e.response.text[:200]
            except Exception:
                pass
            print(f"❌ Falha na autenticação ({e}). Detalhe: {msg}")
            print("Tente novamente.\n")
        except Exception as e:
            print(f"❌ Erro inesperado ao obter token: {e}")
            print("Tente novamente.\n")

# =============================
# PROMPT INTERATIVO DE DATA
# =============================
def interactive_prompt_dates() -> tuple[int, int, list[int]]:
    anos = [2025, 2024, 2023, 2022, 2021]
    print("Selecione o ano:")
    for i, a in enumerate(anos, 1):
        print(f"{i}. {a}")
    while True:
        try:
            ano_idx = int(input("Ano (número): "))
            if 1 <= ano_idx <= len(anos):
                ano = anos[ano_idx - 1]
                break
        except ValueError:
            pass
        print("Entrada inválida. Tente novamente.")
    meses = ["janeiro","fevereiro","março","abril","maio","junho",
             "julho","agosto","setembro","outubro","novembro","dezembro"]
    print("\nSelecione o mês:")
    for i, m in enumerate(meses, 1):
        print(f"{i}. {m}")
    while True:
        try:
            mes = int(input("Mês (número): "))
            if 1 <= mes <= 12:
                break
        except ValueError:
            pass
        print("Entrada inválida. Tente novamente.")
    max_dia = calendar.monthrange(ano, mes)[1]
    print("\nSelecione o dia:")
    print("0. Todos os dias do mês")
    while True:
        try:
            dia = int(input("Dia (número ou 0): "))
            if 0 <= dia <= max_dia:
                break
        except ValueError:
            pass
        print("Entrada inválida. Tente novamente.")
    dias = list(range(1, max_dia + 1)) if dia == 0 else [dia]
    return ano, mes, dias

# =============================
# DOWNLOAD DE JANELA COM PAGINAÇÃO
# =============================
def fetch_activity_window(
    token: str,
    client_id: str,
    client_secret: str,
    from_ts: int,
    to_ts: int,
    limit: int = 1000,
    offset_ceiling: int | None = None,
    verbose: bool = False,
    rate_limiter: RateLimiter | None = None
) -> tuple[list[dict], bool, str]:
    """
    Busca eventos entre from_ts e to_ts (epoch ms), paginando por offset.
    Retorna (eventos, need_minute_fallback, token_atualizado).
    Ativa fallback minuto-a-minuto se:
      - HTTP 400/404; ou
      - offset >= offset_ceiling (Ex.: 10000).
    Faz retry de rede com backoff e renova token em 403 (até 5x).
    """
    offset = 0
    events: list[dict] = []
    need_minute_fallback = False

    consecutive_403 = 0
    max_403_attempts = 5
    max_retries_conn = 5

    while True:
        if offset_ceiling is not None and offset >= offset_ceiling:
            need_minute_fallback = True
            if verbose:
                print(f"   ⚠️ Offset {offset} >= ceiling {offset_ceiling}. Ativando fallback minuto-a-minuto.")
            break

        if rate_limiter:
            rate_limiter.check()

        params = {
            "from": str(from_ts),
            "to": str(to_ts),
            "limit": limit,
            "offset": offset
        }
        headers = {"Authorization": f"Bearer {token}"}

        # Retries para erros de conexão/transientes
        resp = None
        for attempt in range(max_retries_conn):
            try:
                resp = requests.get(ACTIVITY_ENDPOINT, headers=headers, params=params, timeout=60)
                break
            except (requests.exceptions.ConnectionError,
                    requests.exceptions.ChunkedEncodingError,
                    requests.exceptions.ReadTimeout) as e:
                wait = (2 ** attempt)
                print(f"   ⚠️ Erro de conexão ({e}). Tentando novamente em {wait}s...")
                time.sleep(wait)
        if resp is None:
            print("   🚨 Falhas de conexão repetidas. Abortando este intervalo.")
            break

        # Tratamento de retorno
        if resp.status_code == 200:
            try:
                payload = resp.json()
            except Exception as e:
                print(f"   ⚠️ Erro ao decodificar JSON: {e}. Corpo (200 chars): {resp.text[:200]}")
                break

            batch = payload.get("data", [])
            if not batch:
                # sem mais dados
                break

            events.extend(batch)
            offset += len(batch)

            if verbose:
                print(f"      🔹 {len(batch)} eventos (offset agora {offset})")

            consecutive_403 = 0  # reset
            # Se veio menos que limit, acabou a janela
            if len(batch) < limit:
                break

            # continua paginando
            continue

        if resp.status_code == 403:
            consecutive_403 += 1
            print(f"   ⚠️ HTTP 403 detectado ({consecutive_403}/{max_403_attempts}). Renovando token e tentando de novo...")
            try:
                token = get_token(client_id, client_secret)
            except Exception as e:
                print(f"   ❌ Erro ao renovar token: {e}")
                time.sleep(5)  # pequena espera antes de tentar de novo

            if consecutive_403 >= max_403_attempts:
                print("   🚨 403 persistente após várias renovações. Parando este intervalo.")
                break
            # tenta novamente a mesma página
            continue

        if resp.status_code in (400, 404):
            need_minute_fallback = True
            print(f"   ⚠️ HTTP {resp.status_code} — ativando fallback minuto-a-minuto para essa hora.")
            break

        # Outros erros
        print(f"   ⚠️ HTTP {resp.status_code} retornado. Mensagem: {resp.text[:200]}")
        break

    return events, need_minute_fallback, token

# =============================
# BUSCA DA HORA COM FALLBACK DE MINUTO
# =============================
def fetch_hour_with_minute_fallback(
    token: str,
    client_id: str,
    client_secret: str,
    hour_start_dt: datetime,
    limit: int = 1000,
    offset_ceiling: int = 10000,
    verbose: bool = True,
    rate_limiter: RateLimiter | None = None
) -> tuple[list[dict], str]:
    """
    Tenta buscar a hora inteira. Se bater 400/404 ou offset_ceiling,
    cai para minuto-a-minuto (60 chamadas).
    """
    hour_end_dt = hour_start_dt + timedelta(hours=1) - timedelta(milliseconds=1)
    from_ts = dt_to_epoch_millis(hour_start_dt)
    to_ts = dt_to_epoch_millis(hour_end_dt)

    if verbose:
        print(f"\n⏳ Hourly: {fmt_dt(hour_start_dt)} to {fmt_dt(hour_end_dt)}")

    hour_events, need_minute_fallback, token = fetch_activity_window(
        token, client_id, client_secret, from_ts, to_ts,
        limit=limit, offset_ceiling=offset_ceiling, verbose=verbose, rate_limiter=rate_limiter
    )

    if not need_minute_fallback:
        if verbose:
            print(f"   ✅ Hour OK: {len(hour_events)} eventos")
        return hour_events, token

    # Fallback minuto-a-minuto
    collected: list[dict] = []
    if verbose:
        print("   ↪️ Iniciando fallback minuto-a-minuto (60 minutos).")
    for m in range(60):
        minute_start = hour_start_dt + timedelta(minutes=m)
        minute_end = minute_start + timedelta(minutes=1) - timedelta(milliseconds=1)
        m_from = dt_to_epoch_millis(minute_start)
        m_to = dt_to_epoch_millis(minute_end)

        if verbose:
            print(f"      ➤ Minute: {fmt_dt(minute_start)} to {fmt_dt(minute_end)} ... ", end="")

        minute_events, _, token = fetch_activity_window(
            token, client_id, client_secret, m_from, m_to,
            limit=limit, offset_ceiling=None, verbose=False, rate_limiter=rate_limiter
        )
        collected.extend(minute_events)

        if verbose:
            print(f"{len(minute_events)} events")

    if verbose:
        print(f"   ✅ Fallback minute total: {len(collected)} eventos na hora {hour_start_dt.strftime('%Y-%m-%d %H:00')}")
    return collected, token

# =============================
# CSV
# =============================
def _parse_event_datetime(ev: dict) -> datetime | None:
    """
    Tenta montar um datetime do evento:
      - se houver 'timestamp' ISO8601, usa;
      - senão combina 'date' (YYYY-MM-DD) + 'time' (HH:MM:SS), se existirem.
    """
    ts = ev.get("timestamp")
    if isinstance(ts, str) and ts:
        try:
            # aceita "Z" (UTC)
            return datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except Exception:
            pass
    d = ev.get("date")
    t = ev.get("time")
    if isinstance(d, str) and isinstance(t, str):
        try:
            return datetime.fromisoformat(f"{d}T{t}")
        except Exception:
            pass
    return None

def save_to_csv(events: list[dict], filename: str):
    """
    Salva incrementalmente. Colunas fixas + evento bruto serializado.
    """
    file_exists = False
    try:
        with open(filename, "r", encoding="utf-8"):
            file_exists = True
    except FileNotFoundError:
        pass

    with open(filename, "a", newline="", encoding="utf-8") as f:
        fieldnames = ["year", "month", "day", "hour", "timestamp", "event"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()

        for ev in events:
            dt = _parse_event_datetime(ev)
            writer.writerow({
                "year": dt.year if dt else "",
                "month": dt.month if dt else "",
                "day": dt.day if dt else "",
                "hour": dt.hour if dt else "",
                "timestamp": dt.isoformat() if dt else "",
                "event": ev  # dict será serializado como string
            })

# =============================
# MAIN
# =============================
def main():
    # 1) Credenciais com teste
    client_id, client_secret, token = prompt_credentials_with_test()

    # 2) Prompt de datas (ano/mês/dia[s])
    ano, mes, dias = interactive_prompt_dates()
    csv_file = f"activity_{ano}_{mes:02d}.csv"

    start_time = time.time()
    rate_limiter = RateLimiter(max_requests=5000, per_seconds=3600)

    total = 0
    for idx, dia in enumerate(dias):
        print(f"\n📅 Dia: {dia} ({idx+1}/{len(dias)})")
        for hour in range(24):
            hour_start = datetime(ano, mes, dia, hour, 0, 0)
            print(f"⏱️ Tempo decorrido: {elapsed(start_time)}")

            events_hour, token = fetch_hour_with_minute_fallback(
                token, client_id, client_secret, hour_start,
                limit=1000,                # limite seguro/rápido
                offset_ceiling=10000,      # se ultrapassar, cai para minuto-a-minuto
                verbose=True,
                rate_limiter=rate_limiter
            )
            print(f"   ✅ Hour OK: {len(events_hour)} eventos")
            save_to_csv(events_hour, csv_file)
            total += len(events_hour)

    print(f"\n🏁 Concluído! {total} eventos salvos em {csv_file}")
    print(f"⏱️ Tempo total: {elapsed(start_time)}")

if __name__ == "__main__":
    main()
