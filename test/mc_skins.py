import getskin
from PIL import Image

skins_path = '/home/repositories/python/GalacticManager/src/data/skins/'
heads_path = '/home/repositories/python/GalacticManager/src/data/heads/'

img_size = 256
head_offset = 16

class SkinProvider():
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(SkinProvider, cls).__new__(cls)
            return cls.__instance

    @classmethod
    def get_head(cls, username: str) -> str:
        '''
            Get player's skin restorer head

            Returns path to head
        '''
        username = username.lower()
        # Get base64 skin        try:
        skin = getskin.Skin.get_by_username(username)
        skin.download(f'{skins_path}{username}.png')
        print('Use minecraft.com skin')
        # Download skin
        skin.download(f'{skins_path}{username}.png')
        # Open skin with PIL
        skin = Image.open(f'{skins_path}{username}.png')
        # Crop it
        head = skin.crop((8, 8, 16, 16))
        forehead = skin.crop((40, 8, 48, 16))
        # Resize
        head_size = img_size - head_offset * 2
        head = head.resize((head_size, head_size), resample=Image.Resampling.BOX)
        forehead = forehead.resize((img_size, img_size), resample=Image.Resampling.BOX)
        # Generate alpha-image
        alpha = Image.new(mode="RGBA", size=(img_size,img_size), color=(0,0,0,0))
        # Bring together head and forehead
        alpha.paste(head, (head_offset, head_offset))
        alpha.paste(forehead, (0, 0), forehead)
        # Save final head
        alpha.save(f'{heads_path}{username}.png')
        # Return path to head
        return (f'{heads_path}{username}.png')

minecraft_head = SkinProvider()