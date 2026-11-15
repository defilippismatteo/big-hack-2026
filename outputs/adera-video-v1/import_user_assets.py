import hashlib
import json
from pathlib import Path
import shutil
import struct

OUT = Path(__file__).resolve().parent / 'avatars' / 'originals'
OUT.mkdir(parents=True, exist_ok=True)
ATTACHMENTS = Path('/Users/fede/.t3/userdata/attachments')
SOURCES = {
    'portrait-variant-01.png': '4259b5f3-c5ef-4f0c-bc3b-5bf92dfb8173',
    'portrait-glasses.png': '8ae903b3-a002-424e-b59e-ea80a54bbf47',
    'sheet-five-grid.png': '3d8936e6-bb4c-4a58-bc44-984aaa08cf74',
    'sheet-five-row.png': '36204233-e644-4190-8ad2-475d4275f1bf',
    'sheet-ten-grid.png': '480b4144-5bc6-4d34-bb63-677535285d98',
    'chiara-hero.png': '2a00b8e0-0b77-42cb-a293-cad170aaf8e8',
}
manifest = []
for filename, identifier in SOURCES.items():
    source = next(ATTACHMENTS.glob('*' + identifier + '.png'))
    content = source.read_bytes()
    width, height, depth, color_type = struct.unpack('>IIBB', content[16:26])
    shutil.copy2(source, OUT / filename)
    manifest.append({'file': filename, 'source': str(source), 'sha256': hashlib.sha256(content).hexdigest(), 'width': width, 'height': height, 'color_type': color_type, 'alpha_channel_present': color_type in (4, 6), 'status': 'original_imported_not_cleaned'})
(OUT.parent / 'sources.json').write_text(json.dumps(manifest, indent=2))
print(json.dumps(manifest, indent=2))
