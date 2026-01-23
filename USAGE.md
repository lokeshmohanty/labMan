# Lab Management System - User Guide

Complete guide for using the Lab Management System.

## Table of Contents
- [Getting Started](#getting-started)
- [Dashboard](#dashboard)
- [Managing Your Profile](#managing-your-profile)
- [Lab Members](#lab-members)
- [Research Groups](#research-groups)
- [Meetings](#meetings)
- [Content Library](#content-library)
- [Lab Inventory](#lab-inventory)
- [Notifications](#notifications)
- [Mobile Access](#mobile-access)

---

## Getting Started

### First Login
1. Open your web browser
2. Navigate to: `http://localhost:9000`
3. Enter your email and password
4. Click "Login"

### Default Admin Credentials
- **Email**: admin@airex.iisc.ac.in
- **Password**: admin123
- ⚠️ **Change this immediately after first login!**

### Forgot Password?
1. Click "Forgot your password?" on login page
2. Enter your email address
3. Check your email for reset link
4. Click the link and set a new password
5. Login with your new password

---

## Dashboard

Your dashboard shows:
- **Quick Actions**: Common tasks like scheduling meetings, uploading content
- **My Groups**: Research groups you belong to
- **Recent Meetings**: Upcoming and recent meetings
- **System Overview**: Statistics about groups, meetings, and content

### Navigation Bar
Access all features from the top menu:
- **Dashboard**: Home page
- **Members**: Lab members directory
- **Groups**: Research groups
- **Meetings**: Meeting calendar and list
- **Content**: File library
- **Inventory**: Lab equipment and servers
- **Profile**: Your account settings

---

## Managing Your Profile

### Change Password
1. Click **Profile** in navigation bar
2. Select **Change Password**
3. Enter your current password
4. Enter new password (minimum 6 characters)
5. Confirm new password
6. Click "Change Password"

### Email Notifications
Control meeting and content notifications:
1. Click **Profile** → **Settings**
2. Toggle "Email Notifications"
3. When enabled, you'll receive emails for:
   - New meetings you're invited to
   - New content uploaded to meetings
   - Meeting reminders

---

## Lab Members

### View Members
1. Click **Members** in navigation
2. See all lab members with:
   - Name and email
   - Role (Admin/User)
   - Join date

### Add New Member (Admin Only)
1. Click "Add New Member"
2. Fill in:
   - Full name
   - Email address
   - Password
   - Admin checkbox (if admin access needed)
3. Click "Add Member"
4. Share credentials with new member

### Edit Member (Admin Only)
1. Find member in list
2. Click "Edit"
3. Update information
4. Click "Update Member"

### Reset User Password (Admin Only)
1. Find member in list
2. Click "Reset Password"
3. Enter new password
4. Confirm password
5. Click "Reset Password"
6. Inform user of new password securely

---

## Research Groups

### View Groups
Click **Groups** to see all research groups with:
- Group name and description
- Parent group (if hierarchical)
- Member count

### Create Group (Admin Only)
1. Click "Create New Group"
2. Enter:
   - Group name
   - Description
   - Parent group (optional, for hierarchy)
3. Click "Create Group"

### View Group Details
1. Click on any group
2. See members list
3. Admins can add/remove members

### Group Hierarchy Example
```
airex (root)
├── Machine Learning
│   ├── Computer Vision
│   └── Natural Language Processing
└── Robotics
    ├── Robot Perception
    └── Robot Control
```

---

## Meetings

### View Meetings
The Meetings page shows:
- **This Week**: Meetings in the current week
- **Monthly Calendar**: Navigate months with meeting markers
- **Filter by Tags**: Knowledge Session, Research Discussion, Progress Update

### Calendar Features
- **Navigate**: Use arrows to change months
- **Hover**: See meeting details on calendar dates
- **Click**: Go directly to meeting details

### Schedule Meeting
1. Click "Schedule Meeting"
2. Fill in:
   - **Title**: Meeting name
   - **Description**: Agenda and details
   - **Date & Time**: When meeting occurs
   - **Group**: Which research group (optional)
   - **Tags**: Select meeting type
3. Click "Schedule Meeting"

**Meeting Tags:**
- **Knowledge Session**: Learning and teaching
- **Research Discussion**: Research topics
- **Progress Update**: Status updates

### Meeting Details
View meeting information:
- Title, description, time
- Organizer and group
- Attendees and responses
- Meeting materials (uploaded files)

### Respond to Meeting
1. Open meeting details
2. Click "I'll Join" or "Can't Join"
3. Your response is saved
4. Organizer can see who's attending

### Upload Meeting Materials
1. Go to meeting details
2. Click "Upload Materials"
3. Select file
4. Add title and description
5. Click "Upload"

All group members receive email notification when:
- Meeting is scheduled (if notifications enabled)
- New materials are uploaded

---

## Content Library

### View Content
Click **Content** to see all files you have access to:
- Your uploaded files
- Files from your groups
- Public share links

### Filter Content
Use filters to find content:
- **By Group**: Select specific research group
- **By Meeting**: Find meeting materials
- **By Uploader**: See who uploaded

### Upload Content
1. Click "Upload Content"
2. Fill in:
   - **Title**: Content name
   - **Description**: What it contains
   - **File**: Select file (max 100MB)
   - **Group**: Which group can access
   - **Meeting**: Associate with meeting (optional)
   - **Access Level**: 
     - "Group Members Only": Only group members
     - "Anyone with Link": Public sharing
3. Click "Upload Content"

**Allowed file types:**
- Documents: PDF, DOC, DOCX, TXT, MD
- Spreadsheets: XLS, XLSX, CSV
- Presentations: PPT, PPTX
- Images: PNG, JPG, JPEG, GIF
- Code: PY, IPYNB
- Archives: ZIP

### Share Content
For files with "Anyone with Link" access:
1. Find file in content library
2. Click "Copy Link"
3. Share link with anyone
4. They can download without login

### Download Content
1. Find file in content library
2. Click "Download"
3. File downloads to your device

---

## Lab Inventory

### View Inventory
Click **Inventory** to see:
- **Equipment**: Lab equipment and supplies
- **Servers**: Lab servers and infrastructure

### Equipment
See all lab equipment with:
- Name and description
- Quantity (color-coded by stock level)
- Location in lab
- Last updated

**Stock Indicators:**
- 🟢 Green: Well stocked (10+)
- 🟡 Yellow: Medium stock (5-9)
- 🔴 Red: Low stock (<5)

### Servers
View server information:
- **Hostname**: Server name
- **IP Address**: Network address
- **Admin**: Server administrator
- **Location**: Physical location
- **Description**: Server purpose

### Add Equipment (Admin Only)
1. Go to Inventory tab
2. Click "Add Item"
3. Enter:
   - Item name
   - Description
   - Quantity
   - Location
4. Click "Add Item"

### Add Server (Admin Only)
1. Go to Servers tab
2. Click "Add Server"
3. Enter:
   - Hostname
   - IP address
   - Admin name
   - Location
   - Description
4. Click "Add Server"

### Update Inventory (Admin Only)
1. Find item
2. Click "Edit"
3. Update fields
4. Click "Update Item"

---

## Notifications

### Email Notifications
Receive emails for:
- New meeting invitations
- Meeting reminders
- New meeting materials
- Password resets

### Enable/Disable Notifications
1. Click **Profile** → **Settings**
2. Toggle "Email Notifications"
3. Save changes

### Types of Notifications

#### Meeting Created
Sent to all airex group members when new meeting is scheduled:
- Meeting title and description
- Date and time
- Organizer
- Link to meeting details

#### Content Uploaded
Sent when new content is added to a meeting:
- Content title and description
- Meeting information
- Uploader
- Download link

#### Password Reset
Sent when you request password reset:
- Reset link (expires in 24 hours)
- Security instructions

---

## Mobile Access

The system is mobile-friendly and works on:
- Smartphones (iOS, Android)
- Tablets (iPad, Android tablets)
- Desktop browsers

### Mobile Features
- ✅ Responsive design adapts to screen size
- ✅ Touch-friendly buttons and links
- ✅ Easy navigation menu
- ✅ Upload files from mobile
- ✅ View calendar on small screens
- ✅ Download files to mobile

### Mobile Tips
1. **Bookmark**: Add to home screen for quick access
2. **Landscape mode**: Better for calendar view
3. **Downloads**: Files save to downloads folder
4. **Uploads**: Access camera and photo library

---

## Tips & Tricks

### Organize Content
- Use groups to organize by research area
- Link content to meetings for context
- Use descriptive titles and descriptions

### Meeting Management
- Add tags to meetings for easy filtering
- Upload materials before meeting
- Respond to meetings so organizer knows attendance
- Use calendar to plan ahead

### File Sharing
- Use "Anyone with Link" for external collaborators
- Keep group content for internal files
- Name files clearly (e.g., "Q3-Results-2024.pdf")

### Search and Filter
- Use group filters to find relevant content
- Filter meetings by tags
- Check inventory regularly for supplies

---

## Keyboard Shortcuts

### Navigation
- `Alt + D`: Go to Dashboard
- `Alt + M`: Go to Meetings
- `Alt + C`: Go to Content
- `Alt + G`: Go to Groups

### Actions
- `Ctrl + U`: Upload content
- `Ctrl + N`: Schedule new meeting
- `Esc`: Close modal/dialog

---

## Troubleshooting

### Can't Login
- Check email and password spelling
- Use "Forgot password?" if needed
- Ensure Caps Lock is off
- Contact admin if issue persists

### Can't Upload File
- Check file size (max 100MB)
- Verify file type is allowed
- Check internet connection
- Try smaller file or different format

### Email Not Received
- Check spam/junk folder
- Verify email address in profile
- Check notifications are enabled
- Wait a few minutes (may be delayed)

### Can't Access Content
- Verify you're in the correct group
- Check if content is private
- Contact admin for access

### Calendar Not Loading
- Refresh the page
- Clear browser cache
- Try different browser
- Check internet connection

---

## Best Practices

### Security
- Use strong passwords (12+ characters)
- Change password regularly (every 3-6 months)
- Don't share your password
- Log out on shared computers
- Enable email notifications for security alerts

### Content Management
- Upload files promptly after meetings
- Use descriptive titles
- Add proper descriptions
- Tag content with relevant groups
- Keep files organized

### Meetings
- Schedule in advance
- Add clear descriptions
- Use appropriate tags
- Respond to invitations
- Upload materials before meeting

### Communication
- Check dashboard regularly
- Read meeting invitations
- Respond to meeting requests
- Update your profile information
- Enable notifications

---

## Frequently Asked Questions

### Q: How do I change my password?
A: Profile → Change Password. Enter current and new password.

### Q: Can I access from mobile?
A: Yes! The system is fully mobile-responsive.

### Q: How large can uploaded files be?
A: Maximum 100MB per file.

### Q: What file types are supported?
A: Documents, images, spreadsheets, presentations, code files, and archives. See Content Library section for full list.

### Q: How do I share content with external collaborators?
A: Upload with "Anyone with Link" access level, then click "Copy Link" to share.

### Q: Can I turn off email notifications?
A: Yes, in Profile → Settings, toggle Email Notifications.

### Q: How do I know who's attending a meeting?
A: Open meeting details to see responses from all invitees.

### Q: Can I edit uploaded content?
A: You can edit metadata (title, description) but not the file itself. Upload a new version if needed.

### Q: How do I filter meetings?
A: Use tag filters: Knowledge Session, Research Discussion, or Progress Update.

### Q: Where can I see lab servers?
A: Inventory → Servers tab shows all lab servers.

---

## Getting Help

### For General Issues
1. Check this user guide
2. Try troubleshooting steps
3. Ask a colleague
4. Contact system administrator

### For Password Issues
1. Use "Forgot password?" on login
2. Check email for reset link
3. Contact admin if not received

### For Technical Issues
Contact: admin@airex.iisc.ac.in

Include:
- What you were trying to do
- Error message (if any)
- Screenshot (if helpful)
- Browser and device info

---

## Updates and New Features

Check dashboard announcements for:
- New features
- System updates
- Scheduled maintenance
- Important notices

---

**Need more help?** Contact your system administrator at admin@airex.iisc.ac.in
