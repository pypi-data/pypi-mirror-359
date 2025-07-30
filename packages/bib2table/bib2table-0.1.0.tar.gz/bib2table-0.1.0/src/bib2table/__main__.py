from pathlib import Path

import bibtexparser
import click
from bibtexparser.bparser import BibTexParser


DEFAULT_BIB_FILENAME = Path().cwd() / "references.bib"


def escape_latex(s):
    if not s:
        return ""
    return (
        s.replace("&", "\\&")
        .replace("%", "\\%")
        .replace("_", "\\_")
        .replace("#", "\\#")
        .replace("{", "")
        .replace("}", "")
        .replace("$", "\\$")
    )


@click.command
@click.option(
    "--bib-file",
    "-b",
    show_default=True,
    default=DEFAULT_BIB_FILENAME,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
)
def main(bib_file):
    bib_path = Path(bib_file)
    with open(bib_path) as bibtex_file:
        parser = BibTexParser(common_strings=True)
        bib_database = bibtexparser.load(bibtex_file, parser=parser)
    tex_out = bib_path.parent / f"{bib_path.stem}.tex"
    with open(tex_out, "w") as out_file:
        print("saving .tex output to", tex_out)
        print(
            r"""\begin{longtable}{p{1cm}p{6cm}p{1.5cm}p{3cm}p{5cm}}
        \textbf{Variant} & \textbf{Title} & \textbf{Year} & \textbf{Venue} & \textbf{URL} \\
        \hline
        \endfirsthead
        \textbf{Variant} & \textbf{Title} & \textbf{Year} & \textbf{Venue} & \textbf{URL} \\
        \hline
        \endhead
        """,
            file=out_file,
        )

        for entry in bib_database.entries:
            variant = entry["ID"].split("-")[0].upper()
            title = escape_latex(entry.get("title", ""))
            year = escape_latex(entry.get("year", ""))
            venue = escape_latex(
                entry.get("booktitle", "")
                or entry.get("journal", "")
                or entry.get("publisher", "")
            )
            if "doi" in entry:
                doi = entry.get("doi", "").replace("https://doi.org/", "")
                url = f"https://doi.org/{doi}"
            else:
                url = entry.get("url", "")
            print(
                f"    {variant} & {title} & {year} & {venue} & \\url{{{url}}} \\\\",
                file=out_file,
            )

        print(r"\end{longtable}", file=out_file)

    print("done.")


if __name__ == "__main__":
    main()
