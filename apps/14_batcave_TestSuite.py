import os
import shutil
import subprocess
import tempfile
import pytest

MODULES = [
    "01_folder_creator.py",
    "02_pdf_formula_extractor.py",
    "03_overview_generator.py",
    "04_outline_generator.py",
    "05_reasoning_content_generator.py",
    "06_chapter_creator.py",
    "07_folder_filler.py",
    "08_batch_fixer.py",
]

TEST_PROJECT = "TestNovelProject"

# Helper to run a script and capture output/errors
def run_script(script, args=None, cwd=None):
    cmd = ["python3", script]
    if args:
        cmd += args
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return result

@pytest.fixture(scope="module")
def temp_project_dir():
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    shutil.rmtree(tmpdir)

def test_01_folder_creator(temp_project_dir):
    project = os.path.join(temp_project_dir, TEST_PROJECT)
    result = run_script("01_folder_creator.py", ["--project", project], cwd=os.path.dirname(__file__))
    assert os.path.isdir(project)
    for folder in ["overview", "chapters", "notes", "characters", "scenes", "research", "drafts", "synopsis", "outline", "backmatter", "frontmatter"]:
        assert os.path.isdir(os.path.join(project, folder))
    assert os.path.isfile(os.path.join(project, "folder_structure.txt"))

def test_02_pdf_formula_extractor(temp_project_dir):
    # Use a small sample PDF or dummy file for testing
    pdf_path = os.path.join(temp_project_dir, "sample.pdf")
    with open(pdf_path, "wb") as f:
        f.write(b"Dummy PDF content")
    output_path = os.path.join(temp_project_dir, "formula.txt")
    result = run_script("02_pdf_formula_extractor.py", ["--pdf", pdf_path, "--output", output_path], cwd=os.path.dirname(__file__))
    assert os.path.isfile(output_path)

def test_03_overview_generator(temp_project_dir):
    project = os.path.join(temp_project_dir, TEST_PROJECT)
    os.makedirs(os.path.join(project, "overview"), exist_ok=True)
    formula = "Test formula"
    overview_path = os.path.join(project, "overview", "overview.txt")
    result = run_script("03_overview_generator.py", ["--project", project, "--prompt", "A test story", "--formula", formula], cwd=os.path.dirname(__file__))
    assert os.path.isfile(overview_path)

def test_04_outline_generator(temp_project_dir):
    project = os.path.join(temp_project_dir, TEST_PROJECT)
    os.makedirs(os.path.join(project, "overview"), exist_ok=True)
    overview_path = os.path.join(project, "overview", "overview.txt")
    with open(overview_path, "w") as f:
        f.write("Test overview")
    outline_path = os.path.join(project, "master_outline.txt")
    result = run_script("04_outline_generator.py", ["--project", project, "--prompt", "A test story", "--overview", overview_path], cwd=os.path.dirname(__file__))
    assert os.path.isfile(outline_path)

def test_05_reasoning_content_generator(temp_project_dir):
    project = os.path.join(temp_project_dir, TEST_PROJECT)
    outline_path = os.path.join(project, "master_outline.txt")
    overview_path = os.path.join(project, "overview", "overview.txt")
    os.makedirs(os.path.dirname(outline_path), exist_ok=True)
    os.makedirs(os.path.dirname(overview_path), exist_ok=True)
    with open(outline_path, "w") as f:
        f.write("Outline content")
    with open(overview_path, "w") as f:
        f.write("Overview content")
    result = run_script("05_reasoning_content_generator.py", ["--project", project, "--outline", outline_path, "--overview", overview_path], cwd=os.path.dirname(__file__))
    assert os.path.isfile(os.path.join(project, "reasoning_content.md"))

def test_06_chapter_creator(temp_project_dir):
    project = os.path.join(temp_project_dir, TEST_PROJECT)
    chapters_dir = os.path.join(project, "chapters")
    os.makedirs(chapters_dir, exist_ok=True)
    overview_path = os.path.join(project, "overview", "overview.txt")
    with open(overview_path, "w") as f:
        f.write("Overview content")
    result = run_script("06_chapter_creator.py", ["--project", project, "--overview", overview_path], cwd=os.path.dirname(__file__))
    # Check that at least one chapter file was created
    assert any(fname.endswith(".md") for fname in os.listdir(chapters_dir))

def test_07_folder_filler(temp_project_dir):
    project = os.path.join(temp_project_dir, TEST_PROJECT)
    overview_path = os.path.join(project, "overview", "overview.txt")
    os.makedirs(os.path.dirname(overview_path), exist_ok=True)
    with open(overview_path, "w") as f:
        f.write("Overview content")
    result = run_script("07_folder_filler.py", ["--project", project, "--overview", overview_path], cwd=os.path.dirname(__file__))
    # Check that key folders have at least one .md file
    for folder in ["notes", "characters", "scenes", "research", "drafts", "synopsis", "outline", "backmatter", "frontmatter"]:
        folder_path = os.path.join(project, folder)
        if os.path.isdir(folder_path):
            assert any(fname.endswith(".md") for fname in os.listdir(folder_path))

def test_08_batch_fixer(temp_project_dir):
    project = os.path.join(temp_project_dir, TEST_PROJECT)
    chapters_dir = os.path.join(project, "chapters")
    os.makedirs(chapters_dir, exist_ok=True)
    # Remove a chapter file to simulate missing
    missing_chapter = os.path.join(chapters_dir, "chapter_10.md")
    if os.path.exists(missing_chapter):
        os.remove(missing_chapter)
    result = run_script("08_batch_fixer.py", ["--project", project], cwd=os.path.dirname(__file__))
    # Should recreate missing chapter
    assert os.path.isfile(missing_chapter)
