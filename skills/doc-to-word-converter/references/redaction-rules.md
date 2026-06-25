# Redaction Rules for Document Templates

Use these rules when converting real documents (PDF, PPT, Excel, images, DOCX) into reusable templates.

---

## Special Rule: Former Company Name → `****`

**When the document contains the name of the user's former company (i.e. the organization that originally issued or is party to the document), replace every occurrence with exactly four asterisks: `****`.**

- Do NOT use a bracketed placeholder for this. Use `****` literally.
- This lets the user run a single find-and-replace in Word to swap in the correct name.
- Report the total count of `****` replacements in the QA summary.

### Known Former Company Identifiers

> **⚠️ Before using this skill, edit this section to list YOUR OWN former company name.**
> Replace the example entries below with the real company name(s) you want masked as `****`.

Replace ALL of the following with `****`:

- `你的原公司全称`（full legal name, e.g. `XX科技有限公司`）
- `你的原公司简称`（short name commonly used in documents）
- `your-former-company-english-name`（English name, case-insensitive）
- Any variant containing the above identifiers (e.g. `XX电商`, `XX科技`, `XX集团`)

### Auto-Detection Rule

If you encounter a company name containing any of your configured identifiers, treat it as a former-company variant and replace with `****` — **no need to ask the user for confirmation**. Use judgment: if it clearly refers to the same organization, replace it.

---

## Replace Other Sensitive Values with Placeholders

| Sensitive or specific value | Placeholder pattern |
|---|---|
| Other company / legal entity name | `[乙方公司名称]`, `[甲方公司名称]`, `[目标公司名称]` |
| Personal name | `[自然人姓名]`, `[转让方姓名]`, `[受让方姓名]` |
| Unified social credit code | `[统一社会信用代码]` |
| ID / passport number | `[身份证件号码]` |
| Registered address | `[注册地址]` |
| Contact address | `[联系地址]` |
| Phone / mobile | `[联系电话]` |
| Email | `[电子邮箱]` |
| Bank name / account / payment details | `[开户行]`, `[银行账号]`, `[付款信息]` |
| Contract signing date | `[签署日期]` |
| Transfer price / amount | `[转让价款金额]` |
| Equity percentage | `[股权比例]` |
| Payment deadline or period | `[付款期限]` |
| Court / arbitration institution | `[争议解决机构]`, `[仲裁机构]`, `[管辖法院]` |
| City / district tied to the real parties | `[签署地]`, `[管辖地]`, `[注册地址所在地]` |

---

## Checks Before Delivery

- Search for company suffixes that reveal real entities: `有限公司`, `有限责任公司`, `股份有限公司`, `合伙企业`, `个体工商户`.
- Search for long digit/alphanumeric strings (ID numbers, credit codes, phone numbers, bank accounts).
- Search for known party names, source PDF place names, handwritten signature names.
- Confirm `****` appears wherever the former company name was found.
- Confirm all other placeholders are role-based, not derived from real party names.
- Confirm signature pages have editable blank fields only.

---

## Image Retention Rules

**Corner logos and repeated branding → SKIP.** If the same image (icon, logo, decorative element) appears at the same corner position on multiple pages, it is company branding — do NOT OCR it, do NOT embed it in the output Word, and do NOT spend tokens describing it.

- Check: render first 2-3 pages, compare corner positions.
- Applies to: top-left, top-right, bottom-left, bottom-right of every page.
- Applies across all formats: PDF, PPT slides, DOCX headers/footers, single images with corner watermarks.
- Content images (charts, diagrams, photographs in the body) → keep.

---

## What NOT to Redact Blindly

- Keep generic legal terms: `目标公司`, `转让方`, `受让方`, `标的股权`, `本协议`.
- Keep clause numbering and legal obligations (unless they reveal a real transaction value).
- Keep standard legal phrases and governing-law language (after replacing specific court/arbitration details).

---

## Handling Uncertainty

If a phrase may be a real name or may be a generic legal term, do not guess silently. Use a placeholder and note the uncertainty in the QA summary with a `【待确认：...】` tag.
