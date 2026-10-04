# Security Policy

## Scope

The skill itself does not require credentials, private keys, or access tokens to install or use. A target project or agent runtime may have its own credential requirements.

## Reporting a vulnerability

If private vulnerability reporting is unavailable, open a GitHub issue requesting a private reporting channel. Do not include exploit details, secrets, or private project data in the public issue. Once a private channel is established, include the affected file, unsafe behavior, and a minimal reproduction when possible.

## Safety boundaries

- Treat every Server Action and Route Handler as a public endpoint that requires input validation, authentication, and resource-level authorization where applicable.
- Keep server-only data and credentials out of Client Components and browser bundles.
- Validate untrusted navigation targets before passing them to router APIs.
- Prefer installed-version evidence and current official Next.js documentation over remembered framework behavior.
- Installing this skill does not authorize production deployment, credential changes, or other state-changing operations.
