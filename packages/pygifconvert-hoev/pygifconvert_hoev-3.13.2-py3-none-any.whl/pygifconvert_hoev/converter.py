import logging
import glob
from PIL import Image

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)

class GifConverter:
    def __init__(self,path_in=None,path_out=None,resize=(320,240)):
        """
        path_in : 원본 여러 이미지 경로( ex : images/*.png )
        path_out : 결과 이미지 경로( ex : output/filename.gif )
        resize : 리사이징 크기
        """        
        self.path_in = path_in or './*.png' or './*.jpg'
        self.path_out = path_out or './output.gif'
        self.resize = resize
    
    def convert_gif(self):
        """
        GIF 이미지 변환 기능 수행
        """
        logging.info("GIF Converting...")
        logging.info("입력경로 : {}".format(self.path_in))
        logging.info("출력경로 : {}".format(self.path_out))
        logging.info("리사이징 크기 : {}".format(self.resize))
                
        img, *images = [Image.open(f)
                             .resize(self.resize,Image.LANCZOS) 
                             for f in sorted(glob.glob(self.path_in))]
        try:
            img.save(
                fp=self.path_out, 
                format='GIF', 
                append_images=images,
                save_all=True, 
                duration=250, 
                loop=0
            )
            logging.info("GIF Converting done")
        except IOError:
            print('Cannot Convert!', img)

if __name__ == '__main__':
# 직접 파일 실행하면 __main__에서 실행되지만, import됐다면 모듈이름이 main자리에 들어감!
# 배포할때 실행하는 코드는 이런 처리를 해줘야 함!

    # 클래스
    c = GifConverter('./project/images/*png','./project/image_out/result.gif',(320,240))
    # 변환
    c.convert_gif()

