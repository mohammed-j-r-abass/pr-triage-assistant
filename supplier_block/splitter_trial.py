# splitter_trial.py

from supplier_block.document_splitter import text_splitter

texts = """
Secure coding refers to the practice of writing source code for software applications in a manner that actively prevents the introduction of security vulnerabilities. It is a proactive approach integrated throughout the software development lifecycle (SDLC), aiming to build applications resilient against malicious attacks and safeguarding the confidentiality, integrity, and availability (CIA) of data and system resources. This involves adhering to established guidelines and best practices designed to minimize security risks from the initial design phase through implementation, testing, and deployment.
The core objective of secure coding is to prevent common software weaknesses that can be exploited by attackers. These weaknesses often arise from coding errors, design flaws, or misconfigurations. By focusing on security at every stage, developers can build software that inherently protects against unauthorized access, data breaches, denial-of-service attacks, and other cyber threats.
Building secure software relies on adhering to a set of fundamental principles that guide development decisions and practices. These principles form the bedrock of secure coding, aiming to minimize the attack surface and mitigate potential vulnerabilities.
A foundational principle is the rigorous validation of all input data received by an application. Untrusted input, whether from users, external systems, files, or databases, is a primary vector for attacks like Injection (including SQL Injection and XSS) and buffer overflows.
Server-Side Enforcement: All critical validation must occur on a trusted system, typically the server-side, as client-side validation can be easily bypassed.
Allowlisting (Positive Validation): Define precisely what constitutes valid input (e.g., allowed characters, formats, lengths, ranges) and reject anything that does not conform. This is significantly more secure than denylisting (trying to block known bad patterns), which is often incomplete and easily circumvented.
Canonicalization: Convert input data to a standard, simplified form (e.g., decoding URL or HTML encoding, standardizing character sets like UTF-8) before validation to prevent attackers from bypassing checks using encoding tricks. Validation should occur after decoding.
Type, Length, and Range Checks: Verify that input data conforms to the expected data type, falls within acceptable length limits, and is within a valid range or set of values.
Centralized Routine: Implement a centralized validation routine or library to ensure consistency across the application.
Handling Specific Characters: Explicitly check for potentially harmful characters like null bytes, newline characters, and path traversal sequences (../) if they cannot be disallowed by the allowlist.
All validation failures should result in the rejection of the input, and these failures should be logged securely. Output Encoding
Complementary to input validation, output encoding ensures that data sent from the application, particularly data that originated from untrusted sources, is treated as data and not as executable code by the recipient (typically a user's browser). This is the primary defense against Cross-Site Scripting (XSS) attacks. The encoding method must be appropriate for the context in which the data will be rendered (e.g., HTML body, HTML attributes, JavaScript, CSS, URL parameters). Using the wrong encoding type can be ineffective or even introduce new vulnerabilities. HTML entity encoding is common but not universally sufficient.
Server-Side Execution: Encoding operations must be performed on a trusted system (the server) immediately before the data is sent to the client.
Use Standard Libraries: Rely on standard, well-tested encoding libraries (e.g., OWASP Java Encoder, libraries built into modern web frameworks) rather than attempting custom encoding routines.
Encode Untrusted Data: All data originating from untrusted sources that is included in output must be encoded. This includes data retrieved from databases or external systems if its origin or content cannot be fully trusted.
Sanitization for Specific Interpreters: For data destined for interpreters like SQL, LDAP, or OS command shells, contextual sanitization (escaping specific metacharacters) is necessary in addition to input validation.

"""
chunks = text_splitter.split_text(texts)

for i, chunk in enumerate(chunks):
    print(f"Chunk {i+1} (length: {len(chunk)}):\n{chunk}\n")