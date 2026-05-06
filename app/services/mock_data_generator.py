from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


class MockDataGenerator:
    """Generate reproducible mock data for testing."""

    FIRST_NAMES = [
        "Alice",
        "Bob",
        "Carol",
        "David",
        "Eve",
        "Frank",
        "Grace",
        "Henry",
        "Iris",
        "Jack",
        "Karen",
        "Leo",
        "Megan",
        "Noah",
        "Olivia",
        "Peter",
        "Quinn",
        "Rachel",
        "Sam",
        "Tina",
        "Una",
        "Victor",
        "Wendy",
        "Xavier",
        "Yara",
        "Zoe",
    ]

    LAST_NAMES = [
        "Anderson",
        "Bergström",
        "Carlsson",
        "Danielsson",
        "Eriksson",
        "Forsberg",
        "Gustafsson",
        "Hansson",
        "Isaksson",
        "Johansson",
        "Karlsson",
        "Larsson",
        "Mattsson",
        "Nelson",
        "Olsson",
        "Persson",
        "Quick",
        "Rosengren",
        "Svensson",
        "Taberner",
        "Ulfsson",
        "Vilhelm",
        "Wiklund",
        "Xander",
        "Ystrand",
        "Zeller",
    ]

    PRIZE_TITLES = [
        "Abstract Painting",
        "Modern Sculpture",
        "Digital Art Print",
        "Watercolor Landscape",
        "Bronze Figure",
        "Oil Portrait",
        "Mixed Media Collage",
        "Ceramic Vase",
        "Glass Sculpture",
        "Wood Carving",
        "Pastel Drawing",
        "Charcoal Sketch",
        "Ink Installation",
        "Acrylic Canvas",
        "Textile Art",
        "Photographic Print",
        "Metal Etching",
        "Stone Relief",
        "Fiber Art",
        "Installation Piece",
    ]

    PRIZE_DESCRIPTIONS = [
        "A stunning piece exploring color and form",
        "Expertly crafted with attention to detail",
        "Contemporary work from emerging artist",
        "Limited edition artwork",
        "Hand-created original composition",
        "Inspired by nature and movement",
        "Experimental approach to traditional medium",
        "Cultural fusion piece",
        "Thought-provoking contemporary work",
        "Masterfully executed technical piece",
    ]

    @staticmethod
    def generate_mock_participants(output_file: Path, count: int = 100) -> None:
        """Generate mock participant Excel file."""
        try:
            from openpyxl import Workbook
        except ImportError:
            raise RuntimeError("openpyxl is required to generate mock data.")

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "participants"
        sheet.append(["email", "first_name", "last_name"])

        seen_emails = set()
        idx = 0
        while idx < count:
            first = MockDataGenerator.FIRST_NAMES[idx % len(MockDataGenerator.FIRST_NAMES)]
            last = MockDataGenerator.LAST_NAMES[(idx // len(MockDataGenerator.FIRST_NAMES)) % len(MockDataGenerator.LAST_NAMES)]
            email = f"{first.lower()}.{last.lower()}{idx // (len(MockDataGenerator.FIRST_NAMES) * len(MockDataGenerator.LAST_NAMES))}@kulturella.se"
            
            if email not in seen_emails:
                sheet.append([email, first, last])
                seen_emails.add(email)
                idx += 1

        output_file.parent.mkdir(parents=True, exist_ok=True)
        workbook.save(output_file)

    @staticmethod
    def generate_mock_prize_images(output_dir: Path, count: int = 20) -> None:
        """Generate mock prize images."""
        output_dir.mkdir(parents=True, exist_ok=True)

        colors = [
            (230, 126, 34),  # Orange
            (52, 152, 219),  # Blue
            (46, 204, 113),  # Green
            (155, 89, 182),  # Purple
            (236, 100, 75),  # Red
            (241, 196, 15),  # Yellow
            (26, 188, 156),  # Turquoise
            (52, 73, 94),    # Gray-blue
            (211, 84, 0),    # Dark orange
            (44, 62, 80),    # Dark gray
        ]

        for i in range(count):
            image_path = output_dir / f"prize_{i + 1:02d}.png"
            color = colors[i % len(colors)]

            # Create image with solid color background
            image = Image.new("RGB", (400, 300), color)
            draw = ImageDraw.Draw(image)

            # Add text
            text = f"Prize {i + 1}"
            try:
                font = ImageFont.load_default()
            except Exception:
                font = None

            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (400 - text_width) // 2
            y = (300 - text_height) // 2
            draw.text((x, y), text, fill=(255, 255, 255), font=font)

            image.save(image_path)

    @staticmethod
    def generate_mock_prizes(output_file: Path, image_dir: Path, count: int = 20) -> None:
        """Generate mock prize Excel file."""
        try:
            from openpyxl import Workbook
        except ImportError:
            raise RuntimeError("openpyxl is required to generate mock data.")

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "prizes"
        sheet.append(["prize_id", "title", "description", "image_path"])

        for i in range(count):
            prize_id = f"prize_{i + 1:02d}"
            title = MockDataGenerator.PRIZE_TITLES[i % len(MockDataGenerator.PRIZE_TITLES)]
            description = MockDataGenerator.PRIZE_DESCRIPTIONS[i % len(MockDataGenerator.PRIZE_DESCRIPTIONS)]
            image_path = image_dir / f"prize_{i + 1:02d}.png"

            sheet.append([prize_id, title, description, str(image_path)])

        output_file.parent.mkdir(parents=True, exist_ok=True)
        workbook.save(output_file)

    @classmethod
    def generate_all(cls, output_dir: Path, participant_count: int = 100, prize_count: int = 20) -> None:
        """Generate all mock data."""
        data_dir = output_dir / "data"
        participants_dir = data_dir / "participants"
        prizes_dir = data_dir / "prizes"

        cls.generate_mock_participants(participants_dir / "participants.xlsx", participant_count)
        cls.generate_mock_prize_images(prizes_dir / "prize_images", prize_count)
        cls.generate_mock_prizes(prizes_dir / "prizes.xlsx", prizes_dir / "prize_images", prize_count)

        print(f"Generated {participant_count} mock participants in {participants_dir / 'participants.xlsx'}")
        print(f"Generated {prize_count} mock prizes in {prizes_dir / 'prizes.xlsx'}")
        print(f"Generated {prize_count} mock prize images in {prizes_dir / 'prize_images'}")
