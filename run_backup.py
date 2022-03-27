from fileinput import close
import sys, imaplib, os, pprint, datetime, pathlib, shutil 
import lib.common_lib as common
from lib.common_lib import log as log, send_mail_notification
from lib.common_lib import log_error as log_error
from contextlib import closing
from contextlib import redirect_stdout

if os.path.exists(os.path.join('config','configuration.yml')) == False:
    shutil.copyfile(os.path.join('config','template_configuration.yml'), os.path.join('config','configuration.yml'))
if os.path.exists(os.path.join('config','mailboxes_to_backup.yml')) == False:
    shutil.copyfile(os.path.join('config','template_mailboxes_to_backup.yml'), os.path.join('config','mailboxes_to_backup.yml'))
    
config = common.load_configuration(os.path.join('config', 'configuration.yml'))
logFile_timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S%f")
logfile_name = str("mailbackup-"+logFile_timestamp+".log")
logfile_full_path = os.path.join(config['common']['logsFolderFullPath'],logfile_name)

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open(logfile_full_path, "a")
   
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)  

    def flush(self):
        self.log.close()
    
               
sys.stdout = Logger()

log("starting mailbox backup tool")
log("execution folder " +str(pathlib.Path(__file__).parent.resolve()))
log("preparing base directory structure")
output_folder = config['storage']['outputFolderFullPath']
process_folder = config['storage']['processFolderFullPath']
common.create_folder(output_folder)
common.create_folder(process_folder)
mailbox_list_path = os.path.join('config',config['common']['mailboxList'])
mailbox_list = common.open_mailbox_list(mailbox_list_path)
log("found "+str(len(mailbox_list))+" mailboxes in configuration file")
log("======================================================================================================")

for mailbox in mailbox_list.items():
    imap_folders = (str(mailbox[1]['imapFolder'])).split(",")
    
    for imap_folder in imap_folders:
        imap_folder = imap_folder.strip()
        log("preparing to dump all messages from mailbox: " + str(mailbox[0]))
        
        process_mailbox_folder = os.path.join(process_folder, mailbox[0])
        imap_folder_path = os.path.join(process_folder, mailbox[0],imap_folder)
        common.create_folder(process_mailbox_folder)
        common.create_folder(imap_folder_path)
        
        User_is_full_address = mailbox[1]['UserFullEmail']
        if User_is_full_address == True:
            email_user = mailbox[0]
        elif User_is_full_address == False:
            email_user = (mailbox[0]).split('@')[0]
        else:
            log_error("you did not set 'UserFullEmail' parameter in config file. Full email address will be used as username.")
            email_user = mailbox[0]
            
        email_password = mailbox[1]['password']
        imap_host = mailbox[1]['imapHost']
        imap_port = mailbox[1]['imapPort']

        common.save_new_emails_to_eml(host=imap_host, port=imap_port, username=email_user, password=email_password, imap_folder=imap_folder, local_folder=imap_folder_path)
        log("-----------------------------------------------------------------------------------------------------------------")
 

if config['storage']['archiveToZip'] == True:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S%f")
    destination_file_name = str("backup-"+timestamp+".zip")
    common.archive_backup(process_folder, os.path.join(output_folder,destination_file_name))
    zip_existing_test = common.test_path(os.path.join(output_folder,destination_file_name))
    
    if zip_existing_test == True:
        
        if config['storage']['cleanProcessFolder'] == True:
            common.clean_dir(process_folder)
            
if (config['storage']['rollingMethod']).lower() == 'days':
    delete_older_than = config['storage']['deleteOlderBackupThanDays']
    
    if delete_older_than > 0:
        common.roll_backups_days(output_folder,delete_older_than)
        
elif (config['storage']['rollingMethod']).lower() == 'items':
    number_of_items_to_keep = config['storage']['deleteBackupsItemsToKeep']
    
    if number_of_items_to_keep > 0:
        common.roll_backups_items(output_folder,number_of_items_to_keep)
            
if config['mailNotification']['send_notification'] == True:
    log("end of job...sending notification email")
    sys.stdout.flush()
    attachment = [logfile_full_path]
    common.send_mail_notification(send_from=config['mailNotification']['from'],
                        send_to=config['mailNotification']['to'],
                        subject=config['mailNotification']['subject'],
                        text=config['mailNotification']['message'],
                        files=attachment,
                        server=config['mailNotification']['server'],
                        port=config['mailNotification']['port'],
                        username=config['mailNotification']['user'],
                        password=config['mailNotification']['password'],
                        use_tls=config['mailNotification']['useTLS']
                        )
else:
    log("end of job...")