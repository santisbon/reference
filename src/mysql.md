# MySQL development

**Install MySQL Community Edition **
Use your OS package manager or download .dmg installer for macOS. Take note of the root password.

**Configure your PATH**
Add the mysql location to your PATH. Typically as part of your ~/.bash_profile
```zsh
export PATH=/usr/local/mysql/bin:$PATH
```

**Start the MySQL service**
On macOS
```zsh
sudo launchctl load -F /Library/LaunchDaemons/com.oracle.oss.mysql.mysqld.plist
```

**Verify it's running**
On macOS
```zsh
sudo launchctl list | grep mysql
```

**Connect to your MySQL instance**
Use MySQL Workbench or other client tool.

**To stop MySQL**
On macOS
```zsh
sudo launchctl unload -F /Library/LaunchDaemons/com.oracle.oss.mysql.mysqld.plist
```

**Exporting data**
If you need to export data you may need to disable or set a security setting. On macOS:

View the variable using your SQL client. If it's NULL you will be restricted regarding file operations.
```sql
show variables like 'secure_file_priv';
```

Open the configuration file.
```zsh
cd /Library/LaunchDaemons
sudo nano com.oracle.oss.mysql.mysqld.plist
```
and set the --secure-file-priv to an empty string (to disable the restriction) or a dir of your choice.
```xml
<key>ProgramArguments</key>
    <array>
        <string>--secure-file-priv=</string>
    </array>
```

Then restart MySQL. Now you can export data:
```sql
SELECT *
INTO OUTFILE 'your_file.csv'
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
FROM `your_db`.`your_table`
```

You can find your exported data:
```zsh
sudo find /usr/local/mysql/data -name your_file.csv
```

