# 🔗 How to Connect to ai2.trekio.net Server

## Method 1: Using Control Panel SSH Terminal (Recommended)

1. **Open your hosting control panel** at your hosting provider
2. **Click on "SSH Terminal"** in the Dev Tools section
3. **You'll be automatically logged in** as the `trekio` user
4. **Navigate to your web directory**:
   ```bash
   cd /home/trekio/public_html
   ```

## Method 2: Using Local Computer Terminal

### Step 1: Get SSH Access Information
You'll need:
- **Host**: `ai2.trekio.net`
- **Username**: `trekio`
- **Port**: `22` (default)
- **Password**: Your hosting account password

### Step 2: Connect via SSH

#### On Windows (PowerShell/Command Prompt):
```bash
ssh trekio@ai2.trekio.net
```

#### On Mac/Linux Terminal:
```bash
ssh trekio@ai2.trekio.net
```

### Step 3: Enter Password
When prompted, enter your hosting account password.

### Step 4: Navigate to Web Directory
```bash
cd /home/trekio/public_html
```

## Method 3: Using FTP Client (Alternative)

If SSH is not available, you can use FTP:

1. **Use an FTP client** like FileZilla, WinSCP, or Cyberduck
2. **Connection details**:
   - Host: `ai2.trekio.net`
   - Username: `trekio`
   - Password: Your hosting account password
   - Port: `21` (FTP) or `22` (SFTP)

3. **Upload files** to `/public_html/` directory

## Troubleshooting SSH Connection

### If SSH is not enabled:
1. **Contact your hosting provider** to enable SSH access
2. **Check if you need to enable SSH** in your hosting control panel
3. **Verify your hosting plan** includes SSH access

### If you get "Permission denied":
1. **Check your username** - it should be `trekio`
2. **Verify your password** is correct
3. **Try using your hosting account email** as username

### If you get "Connection refused":
1. **Check if SSH is enabled** on your hosting account
2. **Verify the hostname** is correct: `ai2.trekio.net`
3. **Try different ports** (22, 2222, 2200)

## Next Steps After Connection

Once connected, you'll run these commands:

```bash
# 1. Navigate to web directory
cd /home/trekio/public_html

# 2. Upload your project files (see deployment guide)
# 3. Run the setup script
# 4. Configure the application
```
