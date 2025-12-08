# sync-paperpile-notion

Sync changes in Paperpile to a Notion database.

## Setup

### On Notion

1. Create a new database (e.g. "Papers") with the columns named exactly:

    1. `Title` of type title.
    2. `Authors` of type text.
    3. `Year` of type text.
    4. `Link` of type url.
    5. `Reference ID` of type text.

2. Get the **database identifier** from the database page (Copy link to All items). If your database url is:

    ```
    https://www.notion.so/my_workspace/aaaabbbbccccddddeeeeffffgggghhhh
    ```

    Then the database identifier is: `aaaabbbbccccddddeeeeffffgggghhhh`.

3. Create a new integration on [https://www.notion.so/my-integrations/](https://www.notion.so/my-integrations/).

    1. Name: Paperpile to Notion
    2. Associated Workspace: Workspace of the database.
    3. Content Capabilities: Read Content, Update Content, Insert Content.
    4. User Capabilities: Read user information, including email addresses.
    5. Press "Submit" and copy the **Internal Integration Token**.

4. On the database page, click "Connections" (top right) and add "Paperpile to Notion" with edit access.

### On GitHub

1. Fork this repository with the green "Use this template" button.
2. On you fork, go to: "Settings -> Secrets -> Actions".
3. Create 2 new repository secrets named exactly:
    
    1. `NOTION_TOKEN`: Your integration's internal integration token, from step 3.5 above.
    2. `DATABASE_IDENTIFIER`: Your database identifier, from step 2 above.


### On Paperpile

#### Creating an SSH Key

Before setting up the BibTeX Export integration, you need to create an SSH key pair to allow Paperpile to authenticate with GitHub:

1. **Generate an SSH key pair:**

   - **On macOS/Linux:** Open Terminal and run:
     ```bash
     ssh-keygen -t ed25519 -C "paperpile-integration"
     ```
     When prompted for a file location, press Enter to use the default location (`~/.ssh/id_ed25519`).
     When prompted for a passphrase, you can press Enter to skip (no passphrase) for easier automation.

   - **On Windows:** Open PowerShell or Git Bash and run the same command:
     ```bash
     ssh-keygen -t ed25519 -C "paperpile-integration"
     ```
     When prompted for a file location, press Enter to use the default location.
     When prompted for a passphrase, you can press Enter to skip (no passphrase) for easier automation.

2. **Copy your public SSH key:**

   - **On macOS:** Run in Terminal:
     ```bash
     pbcopy < ~/.ssh/id_ed25519.pub
     ```
   
   - **On Linux:** Run in Terminal:
     ```bash
     cat ~/.ssh/id_ed25519.pub
     ```
     Then manually copy the output.
   
   - **On Windows (PowerShell):** Run:
     ```powershell
     Get-Content ~/.ssh/id_ed25519.pub | Set-Clipboard
     ```
   
   - **On Windows (Git Bash):** Run:
     ```bash
     cat ~/.ssh/id_ed25519.pub
     ```
     Then manually copy the output.

3. **Add the SSH key to GitHub:**

   1. Go to GitHub Settings: [https://github.com/settings/keys](https://github.com/settings/keys)
   2. Click "New SSH key" (or "Add SSH key")
   3. Give it a title like "Paperpile Integration"
   4. Paste your public key into the "Key" field
   5. Click "Add SSH key"

4. **Test the SSH connection (optional but recommended):**
   ```bash
   ssh -T git@github.com
   ```
   You should see a message like: "Hi username! You've successfully authenticated..."

#### Setting up BibTeX Export

1. Click on the top-right gear in Paperpile, go to "Workflows and Integrations".
2. Follow the instructions to add a new "BibTex Export", choosing:

    1. Your GitHub repository fork as the repository.
    2. `references.bib` as the export path.
    3. When prompted, provide the **private SSH key** (located at `~/.ssh/id_ed25519` by default).

The first sync should start as soon as the Paperpile workflow is created, and subsequent syncs are triggered whenever papers are added or updated in your Paperpile.

**Note**
The first sync might take some time as Notion limits the API rate to ~ 3 requests / second; so if you have 1,000 papers it'll take ~ 6 minutes before they are all available in Notion.

## Troubleshooting

### SSH Key Issues

**Problem: "Permission denied (publickey)" error**
- Make sure you've added your public SSH key to GitHub at [https://github.com/settings/keys](https://github.com/settings/keys)
- Verify you're using the correct private key file when setting up Paperpile's BibTeX Export
- Test your SSH connection: `ssh -T git@github.com`

**Problem: "Could not open a connection to your authentication agent"**
- Start the SSH agent: `eval "$(ssh-agent -s)"`
- Add your SSH key: `ssh-add ~/.ssh/id_ed25519`

**Problem: SSH key file not found**
- Check if the key file exists: `ls ~/.ssh/id_ed25519`
- If not, generate a new key following the instructions in the "Creating an SSH Key" section above

**Problem: Paperpile can't authenticate with GitHub**
- Ensure you're providing the **private key** (not the .pub file) to Paperpile
- The private key file is typically located at `~/.ssh/id_ed25519` (without the .pub extension)
- On Windows, the path might be `C:\Users\YourUsername\.ssh\id_ed25519`
