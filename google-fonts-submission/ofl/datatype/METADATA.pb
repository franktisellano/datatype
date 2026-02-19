name: "Datatype"
designer: "Frank Tisellano"
license: "OFL"
category: "SANS_SERIF"
date_added: "2026-02-15"

fonts {
  name: "Datatype"
  style: "normal"
  weight: 400
  filename: "Datatype[wdth,wght].ttf"
  post_script_name: "Datatype-Regular"
  full_name: "Datatype Regular"
  copyright: "Copyright 2026 The Datatype Project Authors (https://github.com/franktisellano/datatype)"
}

subsets: "latin"
subsets: "menu"

axes {
  tag: "wdth"
  min_value: 50.0
  max_value: 150.0
}

axes {
  tag: "wght"
  min_value: 100.0
  max_value: 900.0
}

registry_default_overrides {
  key: "wdth"
  value: 100.0
}

registry_default_overrides {
  key: "wght"
  value: 400.0
}

source {
  repository_url: "https://github.com/franktisellano/datatype"
  commit: "5fb35be99482fd663b728f267ea610fe45be7395"
  files {
    source_file: "fonts/variable/Datatype[wdth,wght].ttf"
    dest_file: "Datatype[wdth,wght].ttf"
  }
  files {
    source_file: "OFL.txt"
    dest_file: "OFL.txt"
  }
  branch: "main"
}

stroke: "SANS_SERIF"
classifications: "SYMBOLS"
