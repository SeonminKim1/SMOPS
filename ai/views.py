import io
import boto3
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.utils import timezone

from service.cli import main
from .serializses import AiProductSerializer


class UploadProduct():
    def create_product():
        # input 파일 경로
        base_img_path = "../media/img/base.jpg"
        style_img_path = ["../media/img/style.jpg"]

        # main함수 실행 후 저장
        output_image = main(base_img_path, style_img_path)
        print("===output_image", type(output_image))

        # 파일형식 변환
        in_mem_file = io.BytesIO()
        print(in_mem_file, type(in_mem_file))
        output_image.save(in_mem_file, "PNG")
        in_mem_file.seek(0)
        
        return in_mem_file

    def upload_s3(validated_data):    
        # 파일 업로드
        s3 = boto3.client("s3")
        
        title = validated_data["title"]
        created_user = validated_data["created_user"]
        img_path = validated_data["img_path"]
        
        file_name = f"{created_user}_{title}_{str(timezone.now())}"

        s3.put_object(
            ACL="public-read",
            Bucket="luckyseven-smops",  # "{버킷이름}",
            Body=img_path,  # 업로드할 파일 객체
            Key=file_name,  # S3에 업로드할 파일의 경로
            ContentType="image/png",  # 메타데이터 설정
        )
                

        # url 생성
        bucket_name = "luckyseven-smops"
        key = "output.png"

        s3 = boto3.resource('s3')
        bucket = s3.Bucket(bucket_name)
        location = boto3.client('s3').get_bucket_location(Bucket=bucket_name)['LocationConstraint']
        url = "%s.s3.%s.amazonaws.com/%s" % (bucket_name, location, key)
        
        print("url:", url)
        return url

UploadProduct.create_product()

class AiProductView(APIView):
    def post(self, request):
        request.data["created_user"] = request.user.id
        request.data["owner_user"] = request.user.id
        
        product_serializer = AiProductSerializer(data=request.data)
        product_serializer.is_valid(raise_exception=True)
        product_serializer.save()
        
        return Response(product_serializer.data, status=status.HTTP_200_OK)