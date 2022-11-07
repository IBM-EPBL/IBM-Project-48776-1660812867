cust_mail = email

with smtplib.SMTP("smtp.gmail.com") as connection:
    connection.starttls()
    connection.login(user=mail_id, password=passwd)
    connection.sendmail(
        from_addr=mail_id,
        to_addrs=cust_mail,
        msg="Subject: Hi there "
            "This message is sent from Python."
    )
    connection.quit()