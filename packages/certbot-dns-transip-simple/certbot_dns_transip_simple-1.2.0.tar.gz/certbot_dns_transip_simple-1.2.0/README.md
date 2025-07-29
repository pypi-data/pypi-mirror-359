certbot-dns-transip
=====================

# NO longer maintained, use https://certbot-dns-transip.readthedocs.io/en/stable/ instead

transip_ DNS Authenticator plugin for Certbot

This plugin automates the process of completing a ``dns-01`` challenge by
creating, and subsequently removing, TXT records using the transip Remote API.

Configuration of transip
---------------------------

In `https://www.transip.be/cp/account/api/` you need to have to a keypair


Installation
------------



    pip install certbot-dns-transip-simple


Named Arguments
---------------

To start using DNS authentication for transip, pass the following arguments on
certbot's command line:

`--authenticator certbot-dns-transip:dns-transip`: select the authenticator plugin (Required)

`--dns-transip-credentials`: transip Remote User credentials INI file. (Required)

`--dns-transip-propagation-seconds`: waiting time for DNS to propagate before asking the ACME server to verify the DNS record. Default: 10, Recommended: >= 600)



Credentials
-----------

An example `credentials.ini` file:

```ini
dns_transip_username = myremoteuser
dns_transip_api_key_file = path/to/transip_api_key
```
The path to this file can be provided interactively or using the
`--dns-transip-credentials` command-line argument. Certbot
records the path to this file for use during renewal, but does not store the
file's contents.

**CAUTION:** You should protect these API credentials as you would the
password to your transip account. Users who can read this file can use these
credentials to issue arbitrary API calls on your behalf. Users who can cause
Certbot to run using these credentials can complete a ``dns-01`` challenge to
acquire new certificates or revoke existing certificates for associated
domains, even if those domains aren't being managed by this server.

Certbot will emit a warning if it detects that the credentials file can be
accessed by other users on your system. The warning reads "Unsafe permissions
on credentials configuration file", followed by the path to the credentials
file. This warning will be emitted each time Certbot uses the credentials file,
including for renewal, and cannot be silenced except by addressing the issue
(e.g., by using a command like ``chmod 600`` to restrict access to the file).


Examples
--------

To acquire a single certificate for both `example.com` and
`*.example.com`, waiting 900 seconds for DNS propagation:

```bash

certbot certonly \
   --authenticator dns-transip \
   --dns-transip-credentials /etc/letsencrypt/.secrets/domain.tld.ini \
   --dns-transip-propagation-seconds 900 \
   --server https://acme-v02.api.letsencrypt.org/directory \
   --agree-tos \
   --rsa-key-size 4096 \
   -d 'example.com' \
   -d '*.example.com'
```

```bash
certbot certonly -d 'example.com' -d '*.example.com' --agree-tos  --authenticator dns-transip --dns-transip-credentials=credentials.ini  -n --email=certbot@example.com --dns-transip-propagation-seconds 600
```

It is suggested to secure the folder as follows::
chown root:root /etc/letsencrypt/.secrets
chmod 600 /etc/letsencrypt/.secrets
