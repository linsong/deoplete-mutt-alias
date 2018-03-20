## deoplete-mutt-alias

Mutt alias completion source for
[Deoplete](https://github.com/Shougo/deoplete.nvim).

![screenshot](https://user-images.githubusercontent.com/7629614/37675294-4dbec112-2c4b-11e8-84fb-b02fef350ad9.png)

## Configuration

There is none. This source searches all files in `$XDG_CONFIG_HOME/mutt/` and
`~/.mutt/` and collects aliases from _all_ of them.

## Matching

This source uses a custom matcher. The completion candidates are only gathered
if the current line is a header.

These will all show aliases in the completion menu:

```
To: foo|
Cc: foo|
Bcc: foo|
Subject: foo|
```

This will not:

```
lorem ipsum dolor foo|
```

The matcher also does some magic so the name of the alias is shown in the
completion menu, but not inserted into the buffer. If the menu shows `mom: Jane
Doe <jane.doe@example.com>`, only `Jane Doe <jane.doe@example.com>` will be
inserted into the buffer. This way you can search by alias (`mom`), even if the
alias does not contain words in the name (`Jane Doe`) or email address
(`jane.doe@example.com`) of the person.

Because of the custom matching behavior, I do not recommend overriding the
matcher for this source.

## License

BSD 2-clause
