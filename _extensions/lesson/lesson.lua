-- {{< lesson notebook.py [height=80vh] >}}
-- Embeds an exported marimo notebook (see scripts/export_notebooks.py) with
-- links to open it full-page, download it and open it in molab.

local function read_target(path)
  local f = io.open(path, "r")
  if not f then return nil end
  local text = f:read("a")
  f:close()
  return text:match('#%s*target%s*=%s*"(%w+)"')
end

local function molab_url(repo_url, branch, repo_path, target)
  local base = repo_url:gsub("^https://github%.com/", "https://molab.marimo.io/github/")
  local url = base .. "/blob/" .. branch .. "/" .. repo_path
  if target == "wasm" then url = url .. "/wasm" end
  return url
end

return {
  lesson = function(args, kwargs, meta)
    local file = pandoc.utils.stringify(args[1])
    local stem = file:gsub("%.py$", "")
    local height = pandoc.utils.stringify(kwargs["height"] or "")
    if height == "" then height = "80vh" end

    local doc_dir = pandoc.path.directory(quarto.doc.input_file)
    local target = read_target(pandoc.path.join({ doc_dir, file }))
    if not target then
      error("lesson: cannot read [tool.bb] target from " .. file)
    end

    local project_dir = quarto.project.directory
    local chapter = pandoc.path.make_relative(doc_dir, project_dir):gsub("\\", "/")
    local repo_path = chapter .. "/" .. file
    local book = meta.book or {}
    local repo_url = pandoc.utils.stringify(book["repo-url"] or "")
    local branch = pandoc.utils.stringify(book["repo-branch"] or "main")

    local label = target == "wasm" and "Runs in your browser"
      or "Pre-computed results; run it locally to change it"
    local html = string.format([[
<figure class="bb-lesson">
<iframe src="%s/index.html" title="Lesson notebook: %s" loading="lazy" style="width:100%%;height:%s;border:1px solid var(--bs-border-color);border-radius:6px;"></iframe>
<figcaption class="bb-lesson-links">%s · <a href="%s/index.html" target="_blank" rel="noopener">Open full page</a> · <a href="%s" download>Download notebook</a> · <a href="%s" target="_blank" rel="noopener">Open in molab</a></figcaption>
</figure>]], stem, file, height, label, stem, file, molab_url(repo_url, branch, repo_path, target))
    return pandoc.RawBlock("html", html)
  end,
}
