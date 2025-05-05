import argparse
import asyncio
from email.message import EmailMessage
from aiosmtpd.controller import Controller
import smtplib


class ProxyHandler:
    def __init__(self, smtp_host, smtp_port, smtp_user, smtp_pass, use_tls=True):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_pass = smtp_pass
        self.use_tls = use_tls

    async def handle_DATA(self, server, session, envelope):
        print(f"Received message from: {envelope.mail_from}")
        print(f"To: {envelope.rcpt_tos}")

        try:
            msg = EmailMessage()
            msg.set_content(envelope.content.decode('utf-8', errors='replace'))
            msg['Subject'] = 'Fwd Message'
            msg['From'] = envelope.mail_from
            msg['To'] = ', '.join(envelope.rcpt_tos)

            # Choose correct SMTP class based on port
            if self.smtp_port == 465:
                smtp = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            else:
                smtp = smtplib.SMTP(self.smtp_host, self.smtp_port)
                if self.use_tls:
                    smtp.starttls()

            smtp.login(self.smtp_user, self.smtp_pass)
            smtp.send_message(msg)
            smtp.quit()

            print("Message forwarded successfully.")
            return '250 Message accepted for delivery'

        except Exception as e:
            print(f"Failed to forward message: {e}")
            return f'550 Error: {e}'


def main():
    parser = argparse.ArgumentParser(description="SMTP Proxy (Plain Inbound, TLS/SSL Outbound)")
    parser.add_argument('--listen-port', type=int, required=True, help='Port to listen on (inbound)')
    parser.add_argument('--smtp-host', required=True, help='Upstream SMTP server')
    parser.add_argument('--smtp-port', type=int, default=587, help='Upstream SMTP port')
    parser.add_argument('--smtp-user', required=True)
    parser.add_argument('--smtp-pass', required=True)
    parser.add_argument('--no-tls-outbound', action='store_true', help='Disable STARTTLS when sending upstream (ignored for port 465)')
    args = parser.parse_args()

    handler = ProxyHandler(
        smtp_host=args.smtp_host,
        smtp_port=args.smtp_port,
        smtp_user=args.smtp_user,
        smtp_pass=args.smtp_pass,
        use_tls=not args.no_tls_outbound
    )

    controller = Controller(handler, hostname='0.0.0.0', port=args.listen_port)
    controller.start()

    print(f"SMTP proxy started on port {args.listen_port} (inbound plain SMTP)")
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        print("SMTP proxy stopped.")


if __name__ == '__main__':
    main()
