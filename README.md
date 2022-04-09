# imap_backup_tool

Tool for dumping incrementally emails from many mailboxes to eml files, and make a backup copies in the zip archives. At the end, it will send you an email notification with logs.

# requirements
python - tested on version 3.9.9

## libraries:
Just run:
```pip install -r requirements.txt```

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
  to: 'ziutek@outlook.com'
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

# How is it working

Messages are saved to eml files. A subfolder is created for each mailbox in the process folder. In the mailbox folder, subfolders are created in which messages for imap folders (inbox, sent, etc) are saved.
Message files are named according to the following convention:

    {segment1}__{segment2}__{segment3}.eml

* segment1 - md5 checksum calculated from the message-id field of the message,
* segment2 - first 20 characters of message subject,
* segment3 - time of message.

if segment 3 contains one of the following characters:

    \ "/ ;: <> {}` +, = ~? * |

it is removed. This is because file names cannot contain these characters.

example:

    ec77f17c4c402d3a0a3877559cee51a6__Re M3 Forecast__28-Mar-2022-183517.eml


Before saving the message, it is checked whether such message is already in the folder. If present, it is skipped. This way, all messages are downloaded the first time, and only new messages the next time. The check is only a matter of fetching the Message-id and Date headers, so it's a quick method.

If the archiveToZip parameter is set to True, after the message download is completed, a ZIP archive containing all messages for all defined mailboxes is created and saved to the folder defined in the outputFolderFullPath parameter.

If the cleanProcessFolder parameter is set to True - after each run and archiving to ZIP, all messages will be deleted from the process folder.

The parameters ollingMethod, deleteOlderBackupThanDays, deleteBackupsItemsToKeep are responsible for the method of rolling zip files in the output folder. The DAYS method allows you to define how many last days the files are to be stored. The ITEMS method allows us to define how many files we want to store quantitatively. The methods cannot be combined. The oldest files are deleted.

The parameters ollingMethod, deleteOlderBackupThanDays, deleteBackupsItemsToKeep are responsible for the method of rolling zip files in the output folder. The DAYS method allows you to define how many last days the files are to be stored. The ITEMS method allows us to define how many files we want to store quantitatively. The methods cannot be combined. The oldest files are deleted.

After each run, you can get a message containing a log of the operation progress. The entire mailNotification section is responsible for this.
