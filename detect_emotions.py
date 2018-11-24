import sys
import os
import scipy.io.wavfile
from vokaturi_api import Vokaturi

def create_vokaturi():
	Vokaturi.load("vokaturi_api/OpenVokaturi-3-0-linux64.so")		
		
	def voice2emotions(path2ogg):
		"""
		Takes path to ogg file. Returns object with attributes:
		neutrality, happiness, sadness, anger, fear and their probability.
		"""
		wavpath = path2ogg.replace('ogg', 'wav')
		os.system('ffmpeg -i {0} {1}'\
			.format(path2ogg, wavpath))
		sample_rate, samples = scipy.io.wavfile.read(wavpath)
		buffer_length = len(samples)
		c_buffer = Vokaturi.SampleArrayC(buffer_length)
		if samples.ndim == 1:  # mono
			c_buffer[:] = samples[:] / 32768.0
		else:  # stereo
			c_buffer[:] = 0.5*(samples[:,0]+0.0+samples[:,1]) / 32768.0

		voice = Vokaturi.Voice (sample_rate, buffer_length)
		voice.fill(buffer_length, c_buffer)
		quality = Vokaturi.Quality()
		probs = Vokaturi.EmotionProbabilities()
		voice.extract(quality, probs)

		response = None
		if quality.valid:
			response = emotionProbabilities
		voice.destroy()
		os.system('rm ' + wavpath)
		return response

	return voice2emotions
