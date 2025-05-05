import argparse
import asyncio
from aiosmtpd.controller import Controller
import smtplib
import ssl


class ProxyHandler:
    def __init__(self, smtp_host, smtp_port, smtp_user, smtp_pass, use_tls=True, use_ssl=False):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_pass = smtp_pass
        self.use_tls = use_tls
        self.use_ssl = use_ssl

    async def handle_DATA(self, server, session, envelope):
        print(f"Received message from: {envelope.mail_from}")
        print(f"To: {envelope.rcpt_tos}")

        try:
            if self.use_ssl:
                smtp = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            else:
                smtp = smtplib.SMTP(self.smtp_host, self.smtp_port)
                if self.use_tls:
                    smtp.starttls()

            smtp.login(self.smtp_user, self.smtp_pass)
            smtp.sendmail(
                envelope.mail_from,
                envelope.rcpt_tos,
                envelope.original_content
            )
            smtp.quit()

            print("Message forwarded successfully.")
            return '250 Message accepted for delivery'

        except Exception as e:
            print(f"[!] Failed to forward message: {e}")
            return f'550 Error: {e}'


def main():
    parser = argparse.ArgumentParser(description="SMTP Proxy (Plain Inbound, TLS/SSL Outbound)")
    parser.add_argument('--listen-port', type=int, required=True, help='Port to listen on (inbound)')
    parser.add_argument('--smtp-host', required=True, help='Upstream SMTP server')
    parser.add_argument('--smtp-port', type=int, default=587, help='Upstream SMTP port')
    parser.add_argument('--smtp-user', required=True)
    parser.add_argument('--smtp-pass', required=True)
    parser.add_argument('--no-tls-outbound', action='store_true', help='Disable STARTTLS when sending upstream')
    parser.add_argument('--ssl-outbound', action='store_true', help='Use SSL instead of STARTTLS for upstream')
    args = parser.parse_args()

    handler = ProxyHandler(
        smtp_host=args.smtp_host,
        smtp_port=args.smtp_port,
        smtp_user=args.smtp_user,
        smtp_pass=args.smtp_pass,
        use_tls=not args.no_tls_outbound,
        use_ssl=args.ssl_outbound
    )

    controller = Controller(handler, hostname='0.0.0.0', port=args.listen_port)
    controller.start()

    print(f"SMTP proxy started on port {args.listen_port} (inbound plain SMTP)")
    asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    main()