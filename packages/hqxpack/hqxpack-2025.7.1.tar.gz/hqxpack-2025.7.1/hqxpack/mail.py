import smtplib # 邮件服务
from email.mime.text import MIMEText # 邮件内容
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.mime.image import MIMEImage
     

def sendmail():
    # 发送邮件，不可自定义信息
    msg = MIMEText('bobby') # 邮件内容
    msg['Subject'] = '设备发现异常'
    msg['From'] = '331664089@qq.com'
    msg['To'] = '331664089@qq.com'
    with smtplib.SMTP('smtp.qq.com',587) as s:
        s.starttls()
        s.login('331664089@qq.com','ggvybliyujazbhhd')
        s.sendmail('331664089@qq.com',
                   ['331664089@qq.com',],
                   msg.as_string())
        print('邮件已发送')

# 发送图片
def sendFile(filePath):
    qqMail = smtplib.SMTP_SSL("smtp.qq.com", 465) # 465
    # 2、登陆邮箱
    mailUser = "331664089@qq.com"
    mailPass = "ggvybliyujazbhhd"
    qqMail.login(mailUser, mailPass)
     
    # 3、编辑收发件人
    sender = "331664089@qq.com"
    receiver = "331664089@qq.com"
    # 使用类MIMEMultipart，创建一个实例对象message
    message = MIMEMultipart()
    # 将主题写入 message["Subject"]
    message["Subject"] = Header("您的监测设备发现异常")
    # 将发件人信息写入 message["From"]
    message["From"] = Header(f"haoqixinCloud<{sender}>")
    # 将收件人信息写入 message["To"]
    message["To"] = Header(f"xueqi<{receiver}>")
     
    # 4、构建正文
    # 设置邮件的内容，赋值给变量textContent
    textContent = "请尽快查询"
    # 编辑邮件正文：使用类MIMEText，创建一个实例对象mailContent
    mailContent = MIMEText(textContent, "plain", "utf-8")
     
    with open(filePath, "rb") as imageFile:
        fileContent = imageFile.read()
     
    # 5、设置附件
    attachment = MIMEImage(fileContent)
    # 调用add_header()方法，设置附件标题
    attachment.add_header("Content-Disposition", "attachment", filename="合照.jpg")
    # 添加正文：调用对象message的attach()方法，传入正文对象mailContent作为参数
    message.attach(mailContent)
    # 添加附件：调用对象message的attach()方法，传入附件对象attachment作为参数
    message.attach(attachment)
     
    # 6、发送邮件
    # 发送邮件：使用对象qqMail的sendmail方法发送邮件
    qqMail.sendmail(sender, receiver, message.as_string())
    # 输出"发送成功"
    print("发送成功")

def sendmail_users(alist):
    # 发送邮件，不可自定义信息
    msg = MIMEText('bobby') # 邮件内容
    msg['Subject'] = '设备发现异常'
    msg['From'] = '331664089@qq.com'
    msg['To'] = '331664089@qq.com'
    with smtplib.SMTP('smtp.qq.com',587) as s:
        s.starttls()
        s.login('331664089@qq.com','ggvybliyujazbhhd')
        s.sendmail('331664089@qq.com',alist,
                   msg.as_string())
        print('邮件已发送')

def sendData(info,alist):
    # 发送邮件，并自定义信息
    msg = MIMEText('bobby') # 邮件内容
    msg['Subject'] = info
    msg['From'] = '331664089@qq.com'
    msg['To'] = '331664089@qq.com'
    with smtplib.SMTP('smtp.qq.com',587) as s:
        s.starttls()
        s.login('331664089@qq.com','ggvybliyujazbhhd')
        s.sendmail('331664089@qq.com',
                   alist,
                   msg.as_string())
        print('邮件已发送')
        
