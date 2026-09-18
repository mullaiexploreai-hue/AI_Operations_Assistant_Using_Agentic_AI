INSERT INTO employees VALUES
    ('EMP1024', 'Asha Menon', 'Finance', 'asha.menon@example.com'),
    ('EMP2048', 'Ravi Kumar', 'Engineering', 'ravi.kumar@example.com'),
    ('EMP3072', 'Nisha Shah', 'Operations', 'nisha.shah@example.com');

INSERT INTO knowledge_articles VALUES
    ('KB-001', 'Reset VPN access', 'To reset your VPN access, open the company password portal, choose VPN, and complete MFA verification. Contact IT if MFA is unavailable.', 'vpn password reset access mfa', 'IT Knowledge Base'),
    ('KB-002', 'Request a replacement laptop', 'Submit a hardware ticket with your employee ID, device asset tag, and a short description of the problem. IT will arrange a replacement after verification.', 'laptop hardware replacement device asset', 'IT Knowledge Base'),
    ('KB-003', 'Email outage troubleshooting', 'Check the service status page and restart the mail client. If the outage continues, record the time and create an IT ticket.', 'email outage mail client status', 'IT Knowledge Base');

INSERT INTO support_tickets VALUES
    ('TKT-1001', 'EMP1024', 'VPN disconnects after MFA login', 'network', 'high', 'in_progress', '2026-09-10T09:00:00Z'),
    ('TKT-1002', 'EMP2048', 'Laptop will not start', 'hardware', 'critical', 'open', '2026-09-11T13:30:00Z'),
    ('TKT-1003', 'EMP3072', 'Email messages are delayed', 'email', 'medium', 'resolved', '2026-09-12T15:45:00Z');
