# imap_backup_tool

Tool for dumping emails from mailboxes to eml files. 

# requirements
python - tested on version 3.9.9

##libraries:
Just run:
    pip install -r requirements.txt

# instalation

Just clone this repository, install python, set parameters in configurarion files. 

# configuration

The tool is configurable with two files:
1. the configuration file configuration.yml,
2. a yml file with a list of mailboxes.

## configuration parameters:
```
common:
  rootFolderFullPath: 'c:\mailbox_backup'
  logsFolderFullPath: 'c:\mailbox_backup\logs'
  mailboxList: 'mailboxes_to_backup.yml'

storage:
  processFolderFullPath: 'c:\mailbox_backup\process'
  outputFolderFullPath: 'c:\mailbox_backup\output'
  archiveToZip: True
  cleanProcessFolder: False                            
  rollingMethod: 'DAYS'                                    
  deleteOlderBackupThanDays: 3                              
  deleteBackupsItemsToKeep: 3                               

mailNotification:
  send_notification: True
  server: 'smtp.contoso.com'
  user: 'alerts'
  from: 'alerts@contoso.com'
  password: 'P@$$VV0rD'
  port: 587
  subject: "Notification form MailboxBackupTool"
  to: 'gkonieczko@outlook.com'
  message: 'I would like to inform you that the mailbox copy has been triggered. You will find the logs in the attachment. Do not reply to this message, it was generated automatically.'
  useTLS: True
  ```
I named the parameters in such a way that they explain what they are for, but I will try to describe a few of them in more detail:

- rollingMethod: 'DAYS' - decides that only copies from the last x days will be kept in the OUTPUT folder. This parameter is combined with deleteOlderBackupThanDays in which we set the number of days (value 0 means that no file will be deleted).
- rollingMethod: 'ITEMS' - decides that the specified number of copies will be kept in the OUTPUT folder. This parameter is combined with deleteBackupsItemsToKeep in which we set the number of copies to be kept (value 0 means that no file will be deleted). The oldest files will be deleted.


## mailboxes list
need to be prepared in yml file with following structure:
```
putinmustdie@kremlin.ru:
    UserFullEmail: true
    password: 'FCKIGmurder!'
    imapHost: 'imap.kremlin.com'
    imapPort: 993
    imapFolder: 'inbox,sent'
letsk11l.putin@ukraine.ua:
    UserFullEmail: true
    password: 'Slav@Ukraini'
    imapHost: 'ukraine.ua'
    imapPort: 993
    imapFolder: 'inbox,sent'
```
of course you can add more mailboxes...

# using

example of execution:

    cd c:\mailbox_backup\
    python3 .\run_backup.py

