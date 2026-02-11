# Quick Reference: Get Assigned the Thread Safety Issue

## 🚀 Quick Start (3 Steps)

### 1. Find the Issue
Go to: https://github.com/Prabal864/hive/issues
Look for: Thread safety / Runtime class issues

### 2. Copy the Template
Open: `ISSUE_COMMENT_TEMPLATE.md`
Copy all content

### 3. Post Comment
- Paste in issue comment box
- Add your GitHub username at the bottom
- Click "Comment"

## 📝 What to Say (Template)

```markdown
Hi maintainers! 👋

I'd like to work on fixing the thread safety violations in the Runtime class.

## Problem Summary
1. Unsynchronized state → race conditions
2. Duplicate IDs → TOCTOU bug in dec_{len(decisions)}
3. Silent failures → logger.warning instead of error

## Proposed Fix
1. Add threading.Lock() for synchronization
2. Use UUID-based IDs: dec_{uuid.uuid4().hex[:8]}
3. Elevate to logger.error() for visibility

## Testing
- 9 thread safety tests
- 6 stress tests (1000+ concurrent ops)
- All existing tests pass

## Timeline
~4 days for implementation, testing, and docs

## Request
Could you assign this to me? I'm ready to start immediately!

**Contact**: @YourGitHubUsername
**Availability**: [When you're available]

Thanks! 🙏
```

## ✅ Before Posting Checklist

- [ ] Customized with your GitHub username
- [ ] Added your availability
- [ ] Proofread for typos
- [ ] Ready to start if assigned

## 💬 Expected Response Timeline

- Maintainers typically respond within: 1-3 days
- If no response after 5 days: Politely follow up
- Once assigned: Start work and update regularly

## 🎯 Success Tips

1. **Be specific**: Reference exact files and line numbers
2. **Show understanding**: Explain the race conditions clearly
3. **Be professional**: Friendly but competent tone
4. **Commit to quality**: Mention tests and backward compatibility
5. **Set realistic timeline**: Don't overpromise

## 📧 Alternative: Email Maintainers

If there's no open issue:

**Subject**: Proposal: Fix Thread Safety in Runtime Class

**Body**: Use `PROPOSAL_FOR_MAINTAINERS.md`

**Find emails in**:
- CONTRIBUTING.md
- README.md
- Maintainer GitHub profiles

## 🔗 Useful Links

- **Issue tracker**: https://github.com/Prabal864/hive/issues
- **Contributing guide**: Check CONTRIBUTING.md in repo
- **Your detailed proposal**: See PROPOSAL_FOR_MAINTAINERS.md
- **Implementation guide**: See HOW_TO_PROPOSE.md

## ⚡ Quick Example

**You**: "Hi! I analyzed the Runtime class and found 3 race conditions. I can fix them with threading.Lock + UUID IDs + better logging. Ready to start! Can you assign this to me?"

**Maintainer**: "Sounds good! Few questions: [questions]"

**You**: [Answer questions with details and code examples]

**Maintainer**: "Great! Assigned to you. Looking forward to the PR!"

**You**: "Thank you! I'll have it ready in 4 days with full tests."

---

**Remember**: Show competence through details, be professional, and deliver quality work!

Good luck! 🎉
