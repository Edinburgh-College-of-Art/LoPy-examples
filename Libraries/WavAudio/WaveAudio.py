# =======================================================================================================================
# Writing A WAV file in python
import math

# =======================================================================================================================
class WavAudio:
    """A class for reading and writing audio file in the wav format"""

    header_order = ('chunkID', 'chunkSize', 'waveFormat',
                    'subchunk1ID', 'subChunk1Size', 'audioFormat', 'numChannels',
                    'sampleRate', 'byteRate', 'blockAlign', 'bitsPerSample', 'subchunk2ID', 'subchunk2Size')

    changeable_fields = ('chunkSize', 'byteRate', 'blockAlign', 'subchunk2Size')

    wave_header = {'chunkID': 'RIFF'.encode('utf-8'), 'chunkSize': (0).to_bytes(4, 'little'),
                   'waveFormat': 'WAVE'.encode('utf-8'), 'subchunk1ID': 'fmt '.encode('utf-8'),
                   'subChunk1Size': (16).to_bytes(4, "little"), 'audioFormat': (1).to_bytes(2, "little"),
                   'numChannels': (1).to_bytes(2, "little"), 'sampleRate': (44100).to_bytes(4, "little"),
                   'byteRate': (44100 * 2).to_bytes(4, "little"), 'blockAlign': (2).to_bytes(2, "little"),
                   'bitsPerSample': (16).to_bytes(2, "little"), 'subchunk2ID': 'data'.encode('utf-8'),
                   'subchunk2Size': (44100 * 2).to_bytes(4, "little")}

    # ==================================================================================================================
    # Header sections to update
    # ChunkSize        36 + SubChunk2Size, or more precisely: 4 + (8 + SubChunk1Size) + (8 + SubChunk2Size)
    # ByteRate         == SampleRate * NumChannels * BitsPerSample/8
    # BlockAlign       == NumChannels * BitsPerSample/8
    # Subchunk2Size    == NumSamples * NumChannels * BitsPerSample/8
    # ==================================================================================================================
    # Audio MetaData
    bitDepth = 16
    sampRate = 44100
    channels = 1
    signage = True
    samples = 0  # length in sample numbers: len(Data)
    audioData = []
    audioBytes = []  # The actual sound data: formatted 8/16/32 bits

    # ==================================================================================================================
    # Methods

    def bit_depth_to_bytes(self):
        """convert internal bit depth to byte value"""
        if self.bitDepth == 16:
            bytes_per_samp = 2
        elif (self.bitDepth == 24) | (self.bitDepth == 32):
            bytes_per_samp = 4
        elif self.bitDepth == 8:
            bytes_per_samp = 1
        else:
            bytes_per_samp = 2

        return int(bytes_per_samp)

    def write(self, filename: str, audio: list):
        """ convert audio data to raw bytes and write out to filename"""
        file = open(filename, 'wb')
        bytes_per_samp = self.bit_depth_to_bytes()
        audio = self.normalise(audio)
        self.update_header(len(audio))
        self.audioBytes = [int(math.floor(sample * (pow(2, self.bitDepth-1)-1))) for sample in audio]
        print(bytes_per_samp)
        print(max(self.audioBytes))
        print(max(self.audioBytes).to_bytes(bytes_per_samp, "little", signed=True))

        for field in self.wave_header.keys():
            file.write(self.wave_header[field])

        for sample in self.audioBytes:
            print(sample)
            file.write(sample.to_bytes(bytes_per_samp, "little", signed=True))

        file.close()

    def read(self, filename: str):
        """read audio data from filename into self.audioData"""
        file = open(filename, 'rb')

        for field in self.wave_header.keys():
            self.wave_header[field] = file.read(len(self.wave_header[field]))

        self.print_current_header()
        self.bitDepth = int.from_bytes(self.wave_header['subChunk1Size'], 'little')
        self.sampRate = int.from_bytes(self.wave_header['sampleRate'], 'little')
        self.channels = int.from_bytes(self.wave_header['numChannels'], 'little')

        normal = 1/pow(2, self.bitDepth-1)
        return [bytes * normal for bytes in self.audioBytes]


    def normalise(self, audio: list):
        """normaslise the audio data to use the full range of -1 < x < 1"""
        normal = 1/max(audio)
        return [sample * normal for sample in audio]


    def add_audio_to_file(self):
        """append audio data to an already existing file"""
        # add data and amend the file chunkSize and subchunk2Size
        pass

    def update_header(self, numFrames: int):
        numChannels = int.from_bytes(self.wave_header['numChannels'], "little")
        bitsPerSamp = int.from_bytes(self.wave_header['bitsPerSample'], "little")
        sampleRate = int.from_bytes(self.wave_header['sampleRate'], "little")
        bytesPerFrame = int(numChannels * bitsPerSamp/8)

        self.wave_header['subchunk2Size'] = int(numFrames * bytesPerFrame).to_bytes(4, "little")
        self.wave_header['chunkSize'] = int(36 + (numFrames * bytesPerFrame)).to_bytes(4, 'little')
        self.wave_header['byteRate'] = int(sampleRate * bytesPerFrame ).to_bytes(4, "little")
        self.wave_header['blockAlign'] = int(bytesPerFrame).to_bytes(2, "little")
        # ChunkSize        36 + SubChunk2Size, or more precisely: 36 + SubChunk2Size)
        # ByteRate         == SampleRate * NumChannels * BitsPerSample/8
        # BlockAlign       == NumChannels * BitsPerSample/8
        # Subchunk2Size    == NumSamples * NumChannels * BitsPerSample/8

    # ==================================================================================================================
    # set functions
    def set_audio_quality(self, sample_rate: int, bit_depth: int):
        self.sampRate = sample_rate
        self.wave_header['sampleRate'] = (sample_rate).to_bytes(4, "little")
        self.bitDepth = bit_depth
        self.wave_header['subchunk1Size'] = (bit_depth).to_bytes(4, "little")

    def set_sample_rate(self, sample_rate: int):
        self.sampRate = sample_rate
        self.wave_header['sampleRate'] = (sample_rate).to_bytes(4, "little")

    def set_data(self, data: list):
        """set the internal audio data"""
        self.byteData = [int(math.floor(samp * math.pow(2, (self.bitDepth - 1)))) for samp in data]
        self.samples = len(self.byteData)
        self.wave_header['subChunk2Size'] = int(self.samples * self.channels * self.bitDepth / 8).to_bytes(4, "little")
        self.wave_header['chunkSize'] = (4 + (8 + self.bitDepth) + (8 + int.from_bytes(self.header.subChunk2Size))).to_bytes(4,
                                                                                                                     'little')

    # ==================================================================================================================
    # get functions
    def get_file_sample_rate(self, filename: str):
        """get the sample rate: return sample rate as int"""

        file = open(filename)

    def get_file_header(self, filename: str):
        """get header of a file, return file header object"""
        file = open(filename)

    # ==================================================================================================================
    # print functions
    def print_current_header(self):
        """print out the current object header"""
        for field in self.wave_header.keys():
            print(field + ': {}'.format(int.from_bytes(self.wave_header[field], "little" )))
 
    def print_file_header(self, filename: str):
        file = open(filename, 'rb')
        for field in self.wave_header.keys():
            # print(field + ': {}'.format(int.from_bytes(self.wave_header[field], "little" )))
            print(field + ': {}'.format(   int.from_bytes(file.read(len(self.wave_header[field])), "little" )   ))
        file.close()

# =======================================================================================================================
# write a sine wave
if __name__ == '__main__':
    radsPerSamp = math.pi * 2 * 570 / 44100
    data = [math.sin(s * radsPerSamp) for s in range(84100)]
    filename = 'sine.wav'
    wav = WavAudio()
    wav.write(filename, data)
# EOF
