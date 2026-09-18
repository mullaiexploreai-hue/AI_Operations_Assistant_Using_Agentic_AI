# Demonstration Conversations

Run `python -m db.init_db` before replaying these examples.

## Knowledge search

### Positive: matching article

```text
Employee: How do I reset my VPN password?
Assistant: I found this guidance in IT Knowledge Base, Reset VPN access: To reset your VPN access, open the company password portal, choose VPN, and complete MFA verification. Contact IT if MFA is unavailable.
```

### Positive: another matching article

```text
Employee: What do I need to request a replacement laptop?
Assistant: I found this guidance in IT Knowledge Base, Request a replacement laptop: Submit a hardware ticket with your employee ID, device asset tag, and a short description of the problem. IT will arrange a replacement after verification.
```

### Negative: no matching article

```text
Employee: How do I reserve a parking space?
Assistant: I could not find a matching article in the IT Knowledge Base.
```

### Negative: unsupported request

```text
Employee: Tell me a joke.
Assistant: I can search IT guidance, look up an existing ticket, or create a new ticket. Which would you like?
```

### Boundary: blank or very short query

```text
Employee: Can you search the knowledge base for "a"?
Assistant: I couldn't find a matching IT knowledge article. You can ask me to create a support ticket instead.
```

### Boundary: multiple matching terms

```text
Employee: Email outage and mail client troubleshooting steps, please.
Assistant: I found guidance in the IT Knowledge Base about the email outage and mail client troubleshooting.
```

## Ticket lookup

### Positive: lookup by ticket ID

```text
Employee: I am EMP1024. What is the status of ticket TKT-1001?
Assistant: Ticket TKT-1001 is in_progress. Summary: VPN disconnects after MFA login. Priority: high.
```

### Positive: lookup by issue description

```text
Employee: I am EMP1024. Please check my ticket about VPN disconnects.
Assistant: Ticket TKT-1001 is in_progress. Summary: VPN disconnects after MFA login. Priority: high.
```

### Negative: ticket does not exist

```text
Employee: I am EMP1024. What is the status of ticket TKT-9999?
Assistant: I could not find ticket TKT-9999 for employee EMP1024.
```

### Negative: missing lookup reference

```text
Employee: I am EMP1024. Can you tell me about my support ticket?
Assistant: Please provide a ticket ID or describe the issue so I can find the ticket.
```

### Boundary: ticket ID lookup without issue description

```text
Employee: I am EMP1024. What is the status of ticket TKT-1001?
Assistant: Ticket TKT-1001 is in_progress. Summary: VPN disconnects after MFA login. Priority: high.
```

### Boundary: ID takes precedence over issue text

```text
Employee: I am EMP1024. Check ticket TKT-1001; the issue was email delays.
Assistant: Ticket TKT-1001 is in_progress. Summary: VPN disconnects after MFA login. Priority: high.
```

### Boundary: resolved ticket is still returned

```text
Employee: I am EMP3072. What is the status of my email delay ticket?
Assistant: Ticket TKT-1003 is resolved. Summary: Email messages are delayed. Priority: medium.
```

## Ticket creation

### Positive: create a high-priority ticket

```text
Employee: I am EMP3072 and my laptop will not connect to Wi-Fi. Please create a ticket.
Assistant: Your IT ticket TKT-XXXXXXXX has been created with open status.
```

The generated ticket ID is different on every run. Repeating the same request demonstrates duplicate prevention instead of creating a second open ticket.

### Positive: create with optional details

```text
Employee: I am EMP2048. Create a critical hardware ticket: my replacement laptop will not start.
Assistant: Your IT ticket TKT-XXXXXXXX has been created with open status.
```

### Negative: unknown employee

```text
Employee: I am EMP9999 and my monitor is blank. Please create a ticket.
Assistant: I could not create the ticket because employee EMP9999 was not found.
```

### Negative: missing issue description

```text
Employee: I am EMP1024. Please create a ticket.
Assistant: Please describe the issue before I create the ticket.
```

### Negative: invalid priority

```text
Employee: I am EMP1024. Create a ticket for VPN disconnects with priority urgent.
Assistant: I could not create the ticket because priority must be low, medium, high, or critical.
```

### Boundary: blank employee ID or whitespace-only issue

```text
Employee: Create a ticket for employee "" with issue "   ".
Assistant: Employee ID and issue description are required.
```

### Boundary: duplicate open ticket, case-insensitive summary

```text
Employee: I am EMP3072 and my laptop will not connect to Wi-Fi. Please create a ticket.
Assistant: A matching open ticket already exists: TKT-XXXXXXXX. I did not create a duplicate ticket.

Employee: I am EMP3072 and my LAPTOP WILL NOT CONNECT TO WI-FI. Please create another ticket.
Assistant: A matching open ticket already exists: TKT-XXXXXXXX. I did not create a duplicate ticket.
```

### Boundary: resolved ticket does not block a new ticket

```text
Employee: I am EMP3072 and email messages are delayed. Please create a ticket.
Assistant: Your IT ticket TKT-XXXXXXXX has been created with open status.
```

The last example is allowed because the seeded ticket for the same employee and issue is `resolved`; only matching `open` or `in_progress` tickets are treated as duplicates.
