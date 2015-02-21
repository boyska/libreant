'''
Collection of tests to verify preset paths loading
'''

from nose.tools import raises, eq_
from tempfile import NamedTemporaryFile, mkdtemp
from shutil import rmtree
from presets.presetManager import PresetException
import json
import os
from presets.presetManager import PresetManager


minimalBody = { "id": "id_test",
                    "properties": []
                  }


def test_sigle_file():
    ''' test single file loding'''
    file = NamedTemporaryFile(delete=False)
    file.write(json.dumps(minimalBody))
    file.close()
    p = PresetManager(file.name, strict=True)
    assert minimalBody['id'] in p.presets
    os.unlink(file.name)


def test_multiple_file():
    '''test multiple file loading'''
    files = list()
    presetBodies = list()
    num = 5
    for i in range(0, num):
        files.append(NamedTemporaryFile(delete=False))
        presetBodies.append(minimalBody.copy())
        presetBodies[i]['id'] = "id_" + str(i)
        files[i].write(json.dumps(presetBodies[i]))
        files[i].close()
    p = PresetManager(map(lambda x: x.name, files), strict=True)
    for i in range(0, num):
        assert presetBodies[i]['id'] in p.presets


@raises(PresetException)
def test_duplicate_id():
    f1 = NamedTemporaryFile(delete=False)
    f1.write(json.dumps(minimalBody))
    f1.close()
    f2 = NamedTemporaryFile(delete=False)
    f2.write(json.dumps(minimalBody))
    f2.close()
    p = PresetManager([f1.name,f2.name], strict=True)


def test_empty_path():
    ''' passing empty path must not break anything '''
    p = PresetManager([""])
    eq_(len(p.presets), 0)


@raises(PresetException)
def test_not_existent():
    ''' if preset file do not exists we expect an exception '''
    p = PresetManager("notexistent", strict=True)


def test_folders():
    ''' test preset files distributed in multiple folders '''
    folders = list()
    presetBodies = list()
    num = 5
    for i in range(0, num):
        folders.append(mkdtemp())
        presetBodies.append(minimalBody.copy())
        presetBodies[i]['id'] = "id_" + str(i)
        file = NamedTemporaryFile(delete=False, dir=folders[i])
        file.write(json.dumps(presetBodies[i]))
        file.close()

    p = PresetManager(folders, strict=True)
    for i in range(0, num):
        assert presetBodies[i]['id'] in p.presets
        rmtree(folders[i], ignore_errors=True)

@raises(PresetException)
def test_wrong_json_format():
    ''' if preset has a bad json format we expect an exception'''
    f = NamedTemporaryFile(delete=False)
    f.write("{{{{}")
    f.close()
    p = PresetManager(f.name, strict=True)
