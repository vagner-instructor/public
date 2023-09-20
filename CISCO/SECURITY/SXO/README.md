# Sxo-Amp-Outdated-to-Webex

The main purpose for this project it's to keep the SOC team updated if there's a computer with a problem in the AMP connector.
It was specially designed for Servers, because servers generally keep running 24/7 so basically the Anti Malware Solution should not stop running.

Pro tips: 

* Code Exchange displays the first few content lines of your README in the tile it creates for your repo. If you enter a GitHub Description, Code Exchange uses that instead. 
* Code Exchange works best with READMEs formatted in [GitHub's flavor of Markdown](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax). Support for reStructuredText is a work in progress.

Other things you might include:

* Technology stack: Python, Cisco AMP, Cisco SecureX.
* Status:  1.0
* Screenshot: None


**Sample:**

No Sample.

IMAGE 
![](image_path)

# Use Case (optional)

This automation workflow it's being used for gathering information from Cisco AMP, performing audits and check if server devices has any outdated or amp not running.
It runs everyday day morning and if there's an issue a message is sent to Webex Teams

**Sample:**

No Sample:

- None.
- None.
...


## Installation (required)

Detailed instructions on how to install, configure, and get the project running. Call out any dependencies. This should be frequently tested and updated to make sure it works reliably, accounts for updated versions of dependencies, etc.

**Sample:**

Copy json file
```bash
git clone https://github.com/vagner-instructor/public/tree/b53627d92ac84543867af4bba436c3cab5b68668/CISCO/SECURITY/SXO
```
Go to your SecureX and import as a new Workflow the content in the following json file:

Vagner-Pb0001-Sxo-Amp-Outdated-Webex.json

You'll need:

- CISCO AMP API

- Webex Teams API

- Cisco AMP GROUP GUID 

## Configuration (optional)

You can edit the message sent to SOC, but it's a general message

## Usage (required)

Open Cisco SecureX
Go to Automate
Go to Import as Workflow
Copy the Content from json file (Vagner-Pb0001-Sxo-Amp-Outdated-Webex.json)
Select Import as a Clone
Edit the Variable asked puting Cisco AMP API, Webex Bot API and Cisco AMP GROUP GUID.

**Sample:**

None

## White Paper (optional)
None

## Related Sandbox (optional)
None

Provide a link to a related DevNet Sandbox:
None

## Links to DevNet Learning Labs (optional)
None

## Solutions on Ecosystem Exchange (optional)
None

## Additional paragraphs (optional)
None

## Known issues (optional)
None

## Getting help (optional)

If you're seraching for help please e-mail me vagner.instructor@gmail.com

## Getting involved (optional)
None

## Credits and references (optional)
None

## Best practices

**Information below can help you make your repo meet our requirements and be more useful to others.**

### Good practices

1. Manage sensitive data for scripts. For example, store passwords/API keys and other sensitive data in `env.py` or parse them as arguments. In Python, you can use [ConfigParser](https://docs.python.org/3/library/configparser.html) for applications and programs to encrypt sensitive data in your database.
2. Include in the Installation section how to run your script for different OS like Windows/macOS/Linux.
3. Print usage if you run the script or program without any input data (support -h -help flags).
4. Catch an error and print useful information in the console and interface.
5. Add error management to handle if users miss some parameters or add them in the wrong format.
6. Add links for resources where users can test code/app. For example, add links DevNet sandboxes (Always-on or reservable). You can find a list of all available sandboxes here [https://devnetsandbox.cisco.com/RM/Topology](https://devnetsandbox.cisco.com/RM/Topology).
7. Add links where users can download and how to install additional soft/app/libraries that are needed to run your code. For example, an installer for Python, node, and so on. 
8. Add a NOTICE file with copyright if you use GPLv3 or Apache 2.0 license ([sample NOTICE file](https://github.com/CiscoDevNet/opendaylight-sample-apps/blob/master/NOTICE)).
9. Dockerize app or part of an app like server/client.
10. At the top of the `Readme.md` file add a hash symbol and the full use case name to create a useful Readme title. As an example, write `# Devicebanner, updates the banner motd on a network device` instead of just 'devicebanner'. 
11. If your repo is connected with Cisco SecureX orchestration workflow, please check if your workflow or atomic action conforms to their best practices using [this tool](https://ciscosecurity.github.io/sxo-05-security-workflows/analyzer/).
12. Use [Scorecard](https://github.com/ossf/scorecard) as an easy way to judge whether dependencies in your open source project are safe.

 ### Bad practices
1. Use low quality screenshots.
3. Users need to rename some files like `variables_template.py`.
4. Users need to include credentials in source files.
5. Don’t describe in which format users need to type or paste in file API endpoint or server IP. For example, sometimes devs write in code api_endpoint = “https://" + IP +"/", such that users need to paste the IP only without a slash at the end or a protocol specification. Please clarify this information in README.
