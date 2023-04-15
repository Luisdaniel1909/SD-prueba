#Librerias
from machine import Pin, I2C, ADC
from gpio_lcd import GpioLcd
from ds3231 import DS3231
import utime
import sdcard
import uos

# Configurar los pines y el LCD
lcd = GpioLcd(rs_pin=Pin(8),
              enable_pin=Pin(9),
              d4_pin=Pin(10),
              d5_pin=Pin(11),
              d6_pin=Pin(12),
              d7_pin=Pin(13),
              num_lines=2, num_columns=16)

# Seleccionar el chip (CS) pin (E inicia en alto)
cs = machine.Pin(1, machine.Pin.OUT)

# Inicializa el SPi (Inicia con un 1 MHz)
spi = machine.SPI(0,
                  baudrate=1000000,
                  polarity=0,
                  phase=0,
                  bits=8,
                  firstbit=machine.SPI.MSB,
                  sck=machine.Pin(2),
                  mosi=machine.Pin(3),
                  miso=machine.Pin(4))

# Inicializa La Micro SD
sd = sdcard.SDCard(spi, cs)

# Montar Sistema De archivos
vfs = uos.VfsFat(sd)
uos.mount(vfs, "/sd")

# Definir los pines para el sensor ultrasónico
trig_pin = Pin(17, Pin.OUT)
echo_pin = Pin(16, Pin.IN)

# Configura el RTC
i2c = I2C(0, scl=Pin(21), sda=Pin(20))
rtc = DS3231(i2c)


filename = "/sd/distancia.txt"
with open(filename, "w") as f:
    f.write("Fecha | Hora | Distancia(cm)\n")

while True:
    # Obtener la fecha y hora actual del RTC
    tiempo = rtc.get_time()
    hora = "{:02d}:{:02d}:{:02d}".format(tiempo[3], tiempo[4], tiempo[5])
    fecha = "{:02d}/{:02d}/{:04d}".format(tiempo[2], tiempo[1], tiempo[0])
    
    # Enviar señal al sensor ultrasónico para obtener la distancia
    trig_pin.value(0)
    utime.sleep(0.1)
    trig_pin.value(1)
    utime.sleep_us(2)
    trig_pin.value(0)
    while echo_pin.value()==0:
        pulse_start = utime.ticks_us()
    while echo_pin.value()==1:
        pulse_end = utime.ticks_us()
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17165 / 1000000

    # Imprimir la fecha, hora y distancia en la pantalla LCD
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr(fecha + " " + hora)
    lcd.move_to(0, 1)
    lcd.putstr("Dis: {:.1f} cm".format(distance))

    # Escribir los datos en el archivo
    with open(filename, "a") as f:
        f.write("{} {} {:.1f}\n".format(fecha, hora, distance))
        

    # Esperar un segundo antes de continuar
    utime.sleep(1)

