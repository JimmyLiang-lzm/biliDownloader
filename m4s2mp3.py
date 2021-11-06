import eyed3
import argparse

def read_cover(cover_path:str) -> str:
	with open(cover_path, "rb") as cover:
		return cover.read()

def get_artist() -> str:
	pass

def write_tags():
	mysong = eyed3.load()
	with open() as cover:
		mysong.tag.images.set(3, cover, "image/jpeg")
	mysong.tag.save()