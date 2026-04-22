---
Title: Page layout test
short_title: Layout test
Description: Test the website layout
Date_created: 2025-08-26
---

Introduction paragraph followed by a table of contents.

{% tableOfContents %}

## Headings

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

### Level 3 heading

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

#### Level 4 heading

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

### Heading with [link](https://google.com)

Should work fine

### Heading with [glossary link](/glossary/Anmeldung)

Should work fine

### Heading with €500

Should work fine

### Heading with ellipsis...

Should work fine

### Long heading: Mietschuldenfreiheitsbescheinigung

Wow, that's a doozie! Mietschuldenfreiheitsbescheinigung! Mietschuldenfreiheitsbescheinigung!

## Horizontal rules

Before the `<hr>` element.

---

After the `<hr>` element.

## Custom markup

- Double quotes: "Nice"
- Single quotes: 'Nice'
- Ellipsis: Nice...
- Emdash: Before - after
- Exponentials: Squared^2^, cubed^3^ and other^things^
- Recommended tag:{{ RECOMMENDED }}
- Glossary links: [Anmeldung](/glossary/Anmeldung) and [[Abmeldung]]
- Guide link: [German health insurance](/guides/german-health-insurance)
- Currency: €500
- Marked: <mark>Yellow!</mark>

**[Internal link ➞](/guides/german-health-insurance)**

**[External link ➞](https://nicolasbouliane.com)**

**[Link above ➞](#headings)**

**[Link below ➞](#code)**

## Inline elements

**Bold** and *italic*, `code`.

Footnotes.[^1] Footnotes with formatting.[^2]

## Block elements

### Blockquotes

> **First** line of a blockquote  
> **Second** line of a blockquote

> Separate blockquote

Some paragraph text.

> *Another* blockquote

### Code

    // Some comments
    Indented code
    Second line

Paragraph with `inline code`.

```
Code fences.
Second line.
```

### Lists

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

**Yes-no lists:**

- ✓ Yes
    - ✓ Yes
    - ✗ No
    - Neutral
- ✗ No
    - ✓ Yes
    - ✗ No
    - Neutral
- Neutral
    - ✓ Yes
    - ✗ No
    - Neutral

**Unordered list:**

- Item one
    - Subitem one
- Item two
    - Subitem two
    - Subitem three
        - Subsubitem one
- **Item three**  
    Multiline item!

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

**Ordered list:**

1. Item one
    1. Subitem one
1. Item two
    2. Subitem two
    3. Subitem three
        9. Subsubitem one
2. **Item three**  
    Multiline item!

**Mixed list:**

- [ ] Checklist
    1. Ordered #1
    2. Ordered #2
- Regular
    - [ ] Checklist #1
    - [ ] Checklist #2

### Tables

| Option | Description |
| ------ | ----------- |
| test   | Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. |
| test | test |
| testtesttest    | test |

The table below has aligned columns.

| Center | Right |
| :------:| -----------:|
| data   | path to data files to supply the data that will be passed into templates. |
| engine | engine to be used for processing templates. Handlebars is the default. |
| ext    | extension to be used for dest files. |

### Images

![Alt text only](/images/german-ehic.jpg)

![Captioned](/images/german-ehic.jpg "Image with caption")

Illustrations should not have any border.

![Illustration](/illustrations/mailboxes-briefkasten-germany.png)

[^1]: This is a footnote
[^2]: This is a *footnote* with **formatting** and [links](https://google.com) and [glossary links](/glossary/Anmeldung).