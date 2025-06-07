# FeedSerializer는 피드 전체 정보와 현재 사용자의 좋아요, 북마크 상태를 동적 제공
# FeedImageSerializer는 험부된 이미지 목록을 리스트 형태로 중첩 제공

from rest_framework import serializers
from feed.models import Feed, FeedImage


# 조회용으로 유지
class FeedImageSerializer(serializers.ModelSerializer) : 
    
    class Meta : 
        model = FeedImage
        fields = ['id', 'image', 'order']
    

# 생성 전용
class FeedSerializer(serializers.ModelSerializer) : 
    # user = serializers.SerializerMethodField()    # 작성자 정보
    place = serializers.CharField(required=True, allow_blank=False)   # 장소 정보
    caption = serializers.CharField(required=True, allow_blank=False)   # 캡션
    images = serializers.ListField(child=serializers.ImageField(), write_only=True) #피드 이미지들

    # 좋아요, 북마크, 내 글 관련은 이후 추가할 예정

    class Meta : 
        model = Feed
        fields = ['id', 'place', 'images', 'caption', 'lat', 'lon', 'created_at'] # user 필드는 아직 추가 안 함

    # 빈 값 방지 / 최대 5장 이미지 / 이미지는 장 당 10MB까지
    def validate(self, data):
        if not data.get('place'):
            raise serializers.ValidationError("장소는 반드시 입력해야 합니다.")
        if not data.get('caption'):
            raise serializers.ValidationError("내용은 반드시 입력해야 합니다.")
        
        images = self.context['request'].FILES.getlist('images')
    
        if len(images) > 5:
            raise serializers.ValidationError("이미지는 최대 5개까지만 업로드할 수 있습니다.")
        
        for image in images:
            if image.size > 10 * 1024 * 1024:
                raise serializers.ValidationError("이미지 크기는 최대 10MB까지 허용됩니다.")
        
        return data

    
    def create(self, validated_data):
        images_files = validated_data.pop('images', [])
        lat = validated_data.pop('lat', None)
        lon = validated_data.pop('lon', None)
        feed = Feed.objects.create(**validated_data)

        # 위도/경도 직접 입력값 저장
        if lat and lon :
            feed.lat = lat
            feed.lon = lon
            feed.save()

        return feed


    # def get_user(self, obj):
    #     return {
    #         'id': obj.user.id,
    #         'username': obj.user.username,
    #         # 다른 필드들 필요시 추가
    #     }