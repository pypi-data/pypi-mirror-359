import easyocr
import argparse
import json
import sys
import time
from pathlib import Path
import numpy as np
from tqdm import tqdm


# Configuration Functions
def load_config(config_path):
    """Load configuration from JSON file"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"Error: Config file '{config_path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in config file '{config_path}'.")
        sys.exit(1)


def parse_config(config):
    """Parse and validate configuration, return target_strings and languages"""
    # Handle new config structure with language-organized target strings
    if 'target_strings' in config:
        if isinstance(config['target_strings'], dict):
            # New structure: target_strings organized by language
            languages = list(config['target_strings'].keys())
            target_strings = []
            for lang_strings in config['target_strings'].values():
                if not isinstance(lang_strings, list):
                    raise ValueError("Target strings for each language must "
                                     "be a list.")
                target_strings.extend(lang_strings)
        elif isinstance(config['target_strings'], list):
            # Legacy structure: flat list of target strings
            target_strings = config['target_strings']
            if 'languages' not in config:
                raise ValueError("'languages' field required for legacy "
                                 "config format.")
            languages = config['languages']
        else:
            raise ValueError("'target_strings' must be a list or dictionary "
                             "in config file.")
    elif 'target_string' in config:
        target_strings = [config['target_string']]
        if 'languages' not in config:
            raise ValueError("'languages' field required when using "
                             "'target_string'.")
        languages = config['languages']
    else:
        raise ValueError("Either 'target_string' or 'target_strings' "
                         "required in config file.")

    if not languages:
        raise ValueError("No languages found in config file.")

    case_sensitive = config.get('case_sensitive', False)
    
    return target_strings, languages, case_sensitive


# Utility Functions
def convert_numpy_types(obj):
    """Convert numpy types to JSON serializable Python types"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    return obj


# Text Processing Functions
def check_text_match(detected_text, target_strings, case_sensitive=False):
    """Check if detected text contains any of the target strings"""
    if not case_sensitive:
        detected_text = detected_text.lower()
        target_strings = [s.lower() for s in target_strings]

    matched_strings = []
    for target_string in target_strings:
        if target_string in detected_text:
            matched_strings.append(target_string)
    return matched_strings


# OCR Functions
def initialize_ocr_reader(languages, use_gpu=True, verbose=False):
    """Initialize EasyOCR reader with specified languages"""
    try:
        start_time = time.time()
        reader = easyocr.Reader(languages, gpu=use_gpu)
        end_time = time.time()
        if verbose:
            print(f"OCR reader initialized in {end_time - start_time:.2f} seconds")
        return reader, end_time - start_time
    except Exception as e:
        raise RuntimeError(f"Error initializing OCR reader: {e}")


# Image Processing Functions
def get_image_files(input_path):
    """Get list of image files from input path (file or directory)"""
    input_path = Path(input_path)

    if input_path.is_file():
        supported_formats = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif']
        if input_path.suffix.lower() in supported_formats:
            return [input_path]
        else:
            raise ValueError(f"'{input_path}' is not a supported image "
                             f"format.")

    elif input_path.is_dir():
        image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif']
        image_files = set()

        for ext in image_extensions:
            image_files.update(input_path.glob(f'*{ext}'))
            image_files.update(input_path.glob(f'*{ext.upper()}'))

        return sorted(list(image_files))

    else:
        raise ValueError(f"'{input_path}' does not exist.")


def process_image(image_path, reader, target_strings, case_sensitive=False):
    """Process a single image and check for string matches"""
    try:
        results = reader.readtext(str(image_path))

        matches_found = []
        all_text = []
        matched_strings_set = set()

        for (bbox, text, confidence) in results:
            all_text.append(f"{text} (confidence: {confidence:.2f})")
            matched_strings = check_text_match(text, target_strings,
                                               case_sensitive)
            if matched_strings:
                matches_found.append({
                    'text': text,
                    'confidence': float(confidence),
                    'matched_strings': matched_strings
                })
                matched_strings_set.update(matched_strings)

        return matches_found, all_text, list(matched_strings_set)

    except Exception as e:
        print(f"Error processing image '{image_path}': {e}")
        return [], [], []


# Batch Processing Functions
def process_images_batch(image_files, reader, target_strings,
                         case_sensitive=False, verbose=False):
    """Process multiple images and return consolidated results"""
    start_time = time.time()
    
    total_matches = 0
    all_matched_strings = set()
    images_with_matches = []
    
    # Data structure for results
    results = {
        'summary': {
            'total_images': len(image_files),
            'target_strings': target_strings,
            'case_sensitive': case_sensitive
        },
        'images': []
    }

    # Create progress bar (always visible)
    progress_bar = tqdm(image_files, desc="Processing images", 
                        unit="image")
    
    for image_path in progress_bar:
        progress_bar.set_postfix(file=image_path.name[:30])

        matches, all_text, matched_strings = process_image(
            image_path, reader, target_strings, case_sensitive)

        # Create image result data
        image_result = {
            'filename': image_path.name,
            'filepath': str(image_path),
            'matches': matches,
            'all_text': all_text if verbose else [],
            'matched_target_strings': sorted(matched_strings),
            'match_count': len(matches)
        }

        if matches:
            match_count = len(matches)
            total_matches += match_count
            all_matched_strings.update(matched_strings)
            images_with_matches.append((image_path.name, match_count, 
                                       matched_strings))
            
            # Update progress bar with match info
            progress_bar.set_postfix(file=image_path.name[:20], 
                                   matches=match_count)
        else:
            progress_bar.set_postfix(file=image_path.name[:20], matches=0)

        results['images'].append(image_result)

    end_time = time.time()
    elapsed_time = end_time - start_time

    # Update summary
    results['summary'].update({
        'execution_time_seconds': round(elapsed_time, 2),
        'total_matches': total_matches,
        'images_with_matches': len(images_with_matches),
        'matched_target_strings': sorted(list(all_matched_strings)),
        'unmatched_target_strings': sorted(list(set(target_strings) - all_matched_strings))
    })

    return results, images_with_matches, all_matched_strings, elapsed_time


# Output Functions
def format_and_print_results(results, images_with_matches, all_matched_strings, elapsed_time, show_matches=False, verbose=False):
    """Format and print results to console"""
    image_count = results['summary']['total_images']
    total_matches = results['summary']['total_matches']
    images_with_matches_count = len(images_with_matches)
    target_strings = results['summary']['target_strings']

    print("\n" + "=" * 50)
    print(f"Total images: {image_count}")
    print(f"Summary: Found {total_matches} match(es) in {images_with_matches_count} image(s)")
    print(f"Execution time: {elapsed_time:.2f} seconds")
    
    if images_with_matches:
        print("Images with matches:")
        for image_name, match_count, matched_strings in images_with_matches:
            match_text = "match" if match_count == 1 else "matches"
            matched_str = ", ".join(sorted(matched_strings))
            print(f"  ✓ {image_name} ({match_count} {match_text}) - Matched: [{matched_str}]")
    
    if show_matches and all_matched_strings:
        matched_count = len(all_matched_strings)
        total_targets = len(target_strings)
        print(f"Matched {matched_count}/{total_targets} target strings:")
        for matched_string in sorted(all_matched_strings):
            print(f"  ✓ '{matched_string}'")
        
        unmatched_strings = set(target_strings) - all_matched_strings
        if unmatched_strings:
            print("Unmatched target strings:")
            for unmatched_string in sorted(unmatched_strings):
                print(f"  ✗ '{unmatched_string}'")


def write_json_results(results, output_file):
    """Write results to JSON file"""
    try:
        # Create a clean version for JSON output (only include images with matches)
        json_results = {
            'summary': results['summary'],
            'images': [img for img in results['images'] if img['match_count'] > 0]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_results, f, indent=2, ensure_ascii=False)
        print(f"\nJSON results written to: {output_file}")
        return True
    except Exception as e:
        print(f"Error writing JSON file '{output_file}': {e}")
        return False


# High-level Processing Functions
def run_ocr_analysis(input_path, config_path, verbose=False, show_matches=False, json_output=None, use_gpu=True):
    """
    High-level function to run complete OCR analysis
    
    Args:
        input_path: Path to image file or directory
        config_path: Path to configuration JSON file
        verbose: Show all detected text
        show_matches: Show which target strings were matched
        json_output: Output file for JSON results
        use_gpu: Use GPU for OCR processing
    
    Returns:
        tuple: (results_dict, success_boolean)
    """
    try:
        # Load and parse configuration
        config = load_config(config_path)
        target_strings, languages, case_sensitive = parse_config(config)
        
        # Initialize OCR reader
        reader, init_time = initialize_ocr_reader(languages, use_gpu, verbose)
        
        # Get image files
        image_files = get_image_files(input_path)
        if verbose:
            print(f"Image files: {image_files}")
        
        if not image_files:
            raise ValueError("No image files found to process.")

        if verbose:
            print(f"Processing {len(image_files)} image(s)...")
            print(f"Looking for: {target_strings}")
            print(f"Languages: {languages}")
            print(f"Case sensitive: {case_sensitive}")
            print("-" * 50)

        # Process images
        results, images_with_matches, all_matched_strings, elapsed_time = process_images_batch(
            image_files, reader, target_strings, case_sensitive, verbose)
        
        # Add languages to results
        results['summary']['languages'] = languages
        
        # Print results
        format_and_print_results(results, images_with_matches, all_matched_strings, 
                                elapsed_time, show_matches, verbose)
        
        # Write JSON output if requested
        if json_output:
            write_json_results(results, json_output)
        
        return results, len(images_with_matches) > 0
        
    except Exception as e:
        print(f"Error: {e}")
        return None, False


# CLI Functions
def create_argument_parser():
    """Create and return argument parser for CLI usage"""
    parser = argparse.ArgumentParser(description='OCR text matching tool')
    parser.add_argument('input', help='Path to image file or directory with images')
    parser.add_argument('config', help='Path to configuration JSON file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show all detected text')
    parser.add_argument('--show-matches', '-m', action='store_true', help='Show which target strings were matched')
    parser.add_argument('--json-output', '-j', type=str, help='Output results to JSON file (specify filename)')
    parser.add_argument('--no-gpu', action='store_true', help='Disable GPU acceleration')
    return parser


def main():
    """Main function for CLI usage"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    results, success = run_ocr_analysis(
        input_path=args.input,
        config_path=args.config,
        verbose=args.verbose,
        show_matches=args.show_matches,
        json_output=args.json_output,
        use_gpu=not args.no_gpu
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
