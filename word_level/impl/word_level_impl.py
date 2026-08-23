from models.wordLevelTranscription import WordLevelTranscription
from word_level.word_level_provider import WordLevelProvider
import whisperx
import gc
import warnings
warnings.filterwarnings("ignore")

class WordLevelImpl(WordLevelProvider):
    def generate_word_mapping(self, audio_path: str) -> WordLevelTranscription:
        device = "cpu"
        model_size = "small"  # Options: "tiny", "base", "small", "medium", "large"
        # tiny: ~75MB, base: ~140MB, small: ~460MB, medium: ~1.5GB, large: ~3GB
        
        compute_type = "int8"  
        batch_size = 4 
        
        model = whisperx.load_model(
            model_size, 
            device, 
            compute_type=compute_type,
            language="en" 
        )
        
        audio = whisperx.load_audio(audio_path)

        result = model.transcribe(
            audio, 
            batch_size=batch_size,
            language="en",  
            task="transcribe" 
        )
                
        del model
        gc.collect()

        model_a, metadata = whisperx.load_align_model(
            language_code=result["language"], 
            device=device
        )
        
        result = whisperx.align(
            result["segments"], 
            model_a, 
            metadata, 
            audio, 
            device, 
            return_char_alignments=False
        )
        
        del model_a
        gc.collect()
        
        word_level_transcription = WordLevelTranscription()
        print("results ", result)
        word_level_transcription.segments = result["segments"]
        
        import json
        with open("transcription_output.json", "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        return word_level_transcription