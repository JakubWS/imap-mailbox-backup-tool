
import imaplib, datetime, time, re, requests, yaml, os, email, glob, shutil, mailbox, smtplib, ssl
from zipfile import ZipFile
from email.header import decode_header
from os.path import exists as file_exists
from os.path import basename
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders
from pathlib import Path

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d | %H:%M:%S:%f")
    print(timestamp+" :: [info] "+message)

def log_error(message):

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d | %H:%M:%S:%f")
    print(timestamp+" :: [error]"+message)

def log_fatal(message):

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d | %H:%M:%S:%f")
    print(timestamp+" :: [fatal]"+message)
    quit()
  
def connection_test(url, timeout):
    try:
        request = requests.get(url, timeout=timeout, verify=False)
        return True
    except (requests.ConnectionError, requests.Timeout) as exception:
        return False

def test_path(path):
    if file_exists(path) == True:
        log("path " + path + " exist")
        return True
    else:
        log("path " + path + " not found")
        return False
        
def create_folder(path):
    if test_path(path) == False:
        log("creating directory "+path)
        os.mkdir(path)

def load_configuration(path):
    test_path(path)
    with open(path, "r") as config_file:
        config = yaml.safe_load(config_file)
    return config

def open_mailbox_list(path):
    log("opening mailbox list from " + path)
    test_path(path)
    with open(path, 'r') as mailbox_list:
        mailboxes = yaml.safe_load(mailbox_list)
    return mailboxes

def save_new_emails_to_eml(host, port, username, password, imap_folder, local_folder):
    log("opening connection to the imap server "+host+" on port "+str(port))
    mailbox = imaplib.IMAP4_SSL(host, port)
    mailbox.login(username, password)
    mailbox.select(imap_folder, readonly=True)
    rv, data = mailbox.search(None, "(ALL)")
    log("-- Processing mailbox: " + imap_folder +", found "+str(len(data[0].split()))+" messages")
    new_message_counter = 0
    if rv == 'OK':
    
        for item in data[0].split():
            rv, data = mailbox.fetch(item,'(BODY[HEADER.FIELDS (MESSAGE-ID)])')
            for response_part in data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    message_id = ((msg['message-id']).split("@")[0])[1:]
            
            pattern = str(os.path.join(local_folder,message_id)) + "*.eml"
            new_message_counter = 0        
            if glob.glob(pattern):
                for file in glob.glob(pattern):
                    existing_file_path = os.path.basename(file)
                log("---- found existing message "+ existing_file_path + ". Skipping...")
            else:          
                
                rv, data = mailbox.fetch(item, '(RFC822)')
                for response_part in data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject, encoding = decode_header(msg['subject'])[0] 
                        if encoding != None:
                            subject = subject.decode(encoding)
                        subject = subject[:20]
                        time_of_email = (msg['date'][5:-6]).replace(" ","-")
                        filename = (message_id + "__" + subject + "__" + time_of_email + ".eml")
                        filename = re.sub(r"[\"/;:<>{}`+,=~]", "", filename)
                        filename = re.sub(r"\r\n","__", filename)
                        filename = re.sub(r"\n","__", filename)
                        
                if rv != 'OK':
                    log_error("--- ERROR getting message: "+ str(item))
                    return
                new_message_counter = new_message_counter + 1
                log("------ saving message in file: " + filename)
                file_full_path = os.path.join(local_folder,filename)
                file = open(file_full_path, 'wb')
                file.write(data[0][1])
                file.close()
    else:
        log("ERROR: Unable to open mailbox "+ str(rv))
    log("closing "+ username +" mailbox.")
    
    log("saved "+ str(new_message_counter) + " NEW messages")
    
def archive_backup(source_dir, output_filename):
    relroot = os.path.abspath(os.path.join(source_dir, os.pardir))
    with ZipFile(output_filename, "w") as zip:
        for root, dirs, files in os.walk(source_dir):
            # add directory (needed for empty dirs)
            zip.write(root, os.path.relpath(root, relroot))
            for file in files:
                filename = os.path.join(root, file)
                if os.path.isfile(filename): # regular files only
                    arcname = os.path.join(os.path.relpath(root, relroot), file)
                    zip.write(filename, arcname,compresslevel=9)
                    
def clean_dir(path):
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
            
def roll_backups_days(path, days):
    now = time.time()
    log("Cleaning directory "+path+" from backups older than "+ str(days)+" days.")
    for filename in os.listdir(path):
        if os.path.getmtime(os.path.join(path, filename)) < now - days * 86400:
            if os.path.isfile(os.path.join(path, filename)):
                log("removing old backup: " + filename)
                os.remove(os.path.join(path, filename))
                
def roll_backups_items(path, items_to_keep):
    days = items_to_keep
    log("Cleaning directory "+path+" from backups. Last "+str(items_to_keep)+" backup will be kept")
    list_of_files = sorted(os.listdir(path)[:-days])
    for filename in list_of_files:
        filename_relPath = os.path.join(path,filename)
        log("removing old backup: " + filename_relPath)
        os.remove(filename_relPath)

def send_mail_notification(send_from, send_to, subject, text, files=[],
              server="localhost", port=587, username='', password='',
              use_tls=True):
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = send_to
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject
    msg.attach(MIMEText(text))
    for path in files:
        part = MIMEBase('application', "octet-stream")
        with open(path, 'rb') as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment; filename={}'.format(Path(path).name))
        msg.attach(part)
    smtp = smtplib.SMTP(server, port)
    if use_tls == True:
        context = ssl._create_unverified_context()
        smtp.starttls(context=context)
    smtp.login(username, password)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.quit()