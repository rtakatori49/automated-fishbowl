# Automated Fishbowl

This was created in order to remove the effort required to reserve a fishbowl.

# Initial Setup

1. Clone this repository to a Raspberry Pi in /home/pi

2. Install the required depedencies through requirements.txt

`pip3 install -r requirements.txt`

3. Copy config_template.json and rename to config.json:
    * Reserver: Fill all the users with first and last name and email
    * Fishbowl: Link to reservation site, room to reserve, and times to reserve
    * Email: Credentials of centralized email to accept confirmation email and base link for confirmation link
    * Time Element: Element found with inspect element for beginning time slot
    * OS: Operating system; `windows` for Windows, `raspi` for pi running raspian
    * Debug: Set to `true` for logging debug messages `false` for only error logs

4. Edit crontab to schedule to run every weekday:

`crontab -e`

At the end of the crontab add:

`0 0 * * 1-5 python3 /home/pi/automated-fishbowl/automated_fishbowl.py`

5. Configure each participating reserving user to auto forward the confirmation email to the centralized email.

Follow this link for outlook forwarding: https://www.lifewire.com/forward-outlook-mail-1170648

# Automation
The code was written with the intention of running on a Linux based system running 24/7 with crontab running this script at 00:00:00 every weekday. The script will take in all the configured users to automatically reserve fisbowl spots 2 weeks in advanced. This part is done with selenium. Then those reservation confirmation emails should be forwarded to one centralized email to also be automatically confirmed.