import asyncio
from typing import Any, ClassVar, Dict, Mapping, Optional
from viam.components.sensor import Sensor
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.resource.types import Model, ModelFamily

from enviroplus import gas

import ST7735
from PIL import Image, ImageDraw, ImageFont

class MySensor(Sensor):
    # Subclass the Viam Arm component and implement the required functions
    MODEL: ClassVar[Model] = Model(ModelFamily("tuneni", "sensor"), "enviroplus")

    @classmethod
    def new(cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]):
        sensor = cls(config.name)
        return sensor

    async def get_readings(self, extra: Optional[Dict[str, Any]] = None, **kwargs) -> Mapping[str, Any]:

        nh3_readings = gas.read_nh3()
        ox_readings = gas.read_oxidising()
        red_readings = gas.read_reducing()

        data = {'nh3': nh3_readings, 'ox': ox_readings, 'red': red_readings}
        screen_text = "\n".join(f"{key}: {value}" for key, value in data.items())
        self.lcd_status("Sending GAS readings: \n{}".format(screen_text))

        return data

    def lcd_status(self, text):
        # Create ST7735 LCD display class
        st7735 = ST7735.ST7735(
            port=0,
            cs=1,
            dc=9,
            backlight=12,
            rotation=270,
            spi_speed_hz=10000000
        )

        # Initialize display
        st7735.begin()
        WIDTH = st7735.width
        HEIGHT = st7735.height

        # Set up canvas
        img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Write and display the text at the top in white
        draw.text((0, 0), text, fill=(255, 255, 255))
        st7735.display(img)


async def main():
    gas = MySensor(name="gas")
    signal = await gas.get_readings()
    print(signal)


if __name__ == '__main__':
    asyncio.run(main())
