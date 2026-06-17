import argostranslate.package
import argostranslate.translate


def install_translation_model():

    argostranslate.package.update_package_index()

    packages = argostranslate.package.get_available_packages()

    package = next(
        p for p in packages
        if p.from_code == "en"
        and p.to_code == "zh"
    )

    download_path = package.download()

    argostranslate.package.install_from_path(download_path)


def translate_text(text):

    if not text.strip():
        return ""

    translated = argostranslate.translate.translate(
        text,
        "en",
        "zh"
    )

    return translated