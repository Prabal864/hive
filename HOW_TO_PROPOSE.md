# How to Propose to Maintainers - Step-by-Step Guide

## 📋 Overview

You have **two templates** to use based on the context:

1. **PROPOSAL_FOR_MAINTAINERS.md** - Detailed proposal for email/discussion
2. **ISSUE_COMMENT_TEMPLATE.md** - Concise comment for GitHub issue

## 🎯 When to Use Each Template

### Use PROPOSAL_FOR_MAINTAINERS.md when:
- Emailing maintainers directly
- Starting a discussion thread
- Responding to "tell us more about your approach"
- Submitting a formal proposal

### Use ISSUE_COMMENT_TEMPLATE.md when:
- Commenting on an existing GitHub issue
- Asking to be assigned an issue
- Quick proposal in issue tracker

## 📝 Step-by-Step: Commenting on GitHub Issue

### Step 1: Find the Issue
Go to the repository's Issues page:
```
https://github.com/Prabal864/hive/issues
```

Look for an issue about "thread safety" or "Runtime class race conditions"

### Step 2: Customize the Template

Open `ISSUE_COMMENT_TEMPLATE.md` and personalize:

```markdown
# Replace placeholders:
Hi maintainers! 👋          # Keep this friendly greeting

# At the end, you can add:
**Contact**: @YourGitHubUsername
**Availability**: Available to start immediately / Available evenings and weekends
**Time Zone**: EST / PST / UTC+X
```

### Step 3: Post Your Comment

1. Click on the issue
2. Scroll to the comment box at the bottom
3. Paste the content from `ISSUE_COMMENT_TEMPLATE.md`
4. Click "Comment"

### Step 4: Follow Up

After posting:
- ✅ Watch for maintainer responses (you'll get email notifications)
- ✅ Be ready to answer questions
- ✅ If assigned, acknowledge and confirm your start date

## 📧 Step-by-Step: Emailing Maintainers

### Step 1: Find Maintainer Contact

Check these locations:
- `CONTRIBUTING.md` file in the repository
- Repository README for contact info
- GitHub Discussions tab
- Maintainers' GitHub profiles

### Step 2: Customize the Full Proposal

Open `PROPOSAL_FOR_MAINTAINERS.md` and update:

```markdown
# At the bottom, fill in:
**Contact**: your.email@example.com or @YourGitHubUsername
**Availability**: [Your specific availability]
**Time Zone**: [Your timezone]
```

### Step 3: Send Email

**Subject**: Proposal: Fix Thread Safety Violations in Runtime Class

**Body**: Copy the entire content from `PROPOSAL_FOR_MAINTAINERS.md`

**CC**: If there are multiple maintainers, CC them all

## 💡 Pro Tips for Success

### 1. Show, Don't Just Tell
- ✅ Reference specific code lines (e.g., "line 191 in core.py")
- ✅ Include code snippets showing the issue
- ✅ Demonstrate understanding with examples

### 2. Be Professional & Respectful
- ✅ Use friendly, professional tone
- ✅ Thank them for their time
- ✅ Be patient waiting for response
- ❌ Don't demand or be pushy

### 3. Demonstrate Competence
- ✅ Show you've analyzed the code
- ✅ Mention specific files and line numbers
- ✅ Explain the technical details clearly
- ✅ Reference similar issues in other projects

### 4. Make It Easy for Them
- ✅ Clear, structured proposal
- ✅ Specific timeline
- ✅ Low-risk approach
- ✅ Offer to discuss further

### 5. Build Trust
- ✅ Link to your GitHub profile with previous contributions
- ✅ Mention relevant experience
- ✅ Show you understand their codebase
- ✅ Commit to following their conventions

## 🎬 Example Workflow

Here's a typical interaction:

### You Comment:
```
[Use ISSUE_COMMENT_TEMPLATE.md content]
```

### Maintainer Responds:
```
"Thanks for the detailed proposal! A few questions:
1. How will you handle the case where...
2. What about backward compatibility with...
3. Can you show an example of..."
```

### You Reply:
```
"Great questions! Here are my thoughts:

1. For the case where X happens, I would...
   [code example]

2. Backward compatibility is maintained because...
   [explanation]

3. Here's a concrete example:
   [code snippet]

I'm happy to discuss further or provide more details!"
```

### Maintainer Assigns:
```
"Thanks for the thorough response. Assigning this to you.
Looking forward to the PR!"
```

### You Acknowledge:
```
"Thank you! I'll start working on this today and will
have a PR ready within 4 days. I'll keep you updated
on progress."
```

## 🚨 Common Mistakes to Avoid

❌ **Don't**: Just say "I can fix this"  
✅ **Do**: Show HOW you'll fix it with details

❌ **Don't**: Make unsubstantiated claims  
✅ **Do**: Reference specific code and tests

❌ **Don't**: Promise unrealistic timelines  
✅ **Do**: Give conservative, achievable estimates

❌ **Don't**: Ignore maintainer questions  
✅ **Do**: Respond promptly and thoroughly

❌ **Don't**: Start working before being assigned  
✅ **Do**: Wait for confirmation to avoid wasted effort

## 📊 What Maintainers Look For

Maintainers want to see:

1. **Understanding** - You comprehend the issue deeply
2. **Planning** - You have a clear, thoughtful approach
3. **Testing** - You prioritize quality and testing
4. **Communication** - You can explain technical details clearly
5. **Reliability** - You'll follow through on commitments
6. **Collaboration** - You're open to feedback

## 🎓 Additional Resources

If maintainers ask for more details, you can reference:

- `core/framework/runtime/THREAD_SAFETY.md` - Complete thread safety analysis
- `core/framework/runtime/tests/test_runtime_thread_safety.py` - Example tests
- `core/framework/runtime/tests/test_runtime_stress.py` - Stress test examples

## ✅ Checklist Before Posting

Before submitting your proposal, verify:

- [ ] I've read the existing issue thoroughly
- [ ] I've checked if someone else is already assigned
- [ ] I've customized the template with my details
- [ ] I've proofread for typos and clarity
- [ ] I've checked my tone is professional and friendly
- [ ] I'm available to start work if assigned
- [ ] I'm prepared to answer follow-up questions

## 🎉 Good Luck!

Remember:
- Be confident but humble
- Show expertise through details
- Make it easy for maintainers to say yes
- Be ready to prove yourself with great code

You've got this! 💪
