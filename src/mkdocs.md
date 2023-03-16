# MkDocs

For full documentation visit [mkdocs.org](https://www.mkdocs.org).

```zsh
pip install mkdocs python-markdown-math mkdocs-material
```

## Commands

* `mkdocs new [dir-name]` - Create a new project.
* `mkdocs serve` - Start the live-reloading docs server.
* `mkdocs build` - Build the documentation site.
* `mkdocs -h` - Print help message and exit.

## Default project layout

    mkdocs.yml    # The configuration file.
    docs/
        index.md  # The documentation homepage.
        ...       # Other markdown pages, images and other files.

## Themes

Included: `mkdocs`, `readthedocs`.  
Third-party: `material`.

## Extensions

[Documentation](https://python-markdown.github.io/extensions/)  

### Admonition
[Documentation](https://python-markdown.github.io/extensions/admonition/)  
Types: `attention`, `caution`, `danger`, `error`, `hint`, `important`, `note`, `tip`, and `warning`. The text must be indented.

```
!!! hint
    Text goes here.
```
!!! hint
    Text goes here.

### Keys
[Documentation](https://facelessuser.github.io/pymdown-extensions/extensions/keys/#extendingmodifying-key-map-index)
```
++command+shift+n++
```
++command+shift+n++

### MathJax

```
When \(a \ne 0\), there are two solutions to \(ax^2 + bx + c = 0\) and they are
$$x = {-b \pm \sqrt{b^2-4ac} \over 2a}$$
```
When \(a \ne 0\), there are two solutions to \(ax^2 + bx + c = 0\) and they are
$$x = {-b \pm \sqrt{b^2-4ac} \over 2a}$$
