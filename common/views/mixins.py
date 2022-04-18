from tempfile import NamedTemporaryFile

from django.core.paginator import Paginator
from django.http import Http404, FileResponse
from django_filters import rest_framework as filters
from openpyxl import Workbook

from common.views.resp import JSONResponse


class GeneralCodeMixin:
    CODE_OK = 0
    CODE_INVALID_PARAMS = 400
    CODE_USER_NOT_EXISTS = 401
    CODE_RESOURCE_NOT_FOUND = 404
    CODE_NEED_LOGIN = 412
    CODE_NEED_RESET_PW = 413
    CODE_GENERAL_ERROR = 500
    CODE_NOT_PERMITTED = 444
    CODE_COUPON_DELETE_FAIL = 450

    DEFAULT_MSG = {
        CODE_RESOURCE_NOT_FOUND: '不存在的资源',
        CODE_NOT_PERMITTED: '不允许的操作'
    }


class BaseAPIViewMixin:

    @classmethod
    def resp_payload(cls, code, data=None, msg=None):
        if not msg and code in cls.DEFAULT_MSG:
            msg = cls.DEFAULT_MSG.get(code)
        return {'code': code, 'data': data, 'msg': msg}

    # Response with http status code 200
    def ok_resp(self, code, data=None, msg=None):
        payload = self.resp_payload(code, data, msg)
        return JSONResponse(payload)

    # Response with http status code non-200
    def non_ok_resp(self, status, code=None, data=None, msg=None):
        payload = self.resp_payload(code, data, msg) if code else None
        return JSONResponse(payload, status=status)


class RetrieveModelMixin(BaseAPIViewMixin):
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return self.ok_resp(self.CODE_RESOURCE_NOT_FOUND)

        serializer = self.get_serializer(instance, many=False)
        return self.ok_resp(self.CODE_OK, data={'item': serializer.data})


class ListModelMixin(BaseAPIViewMixin):
    enable_pagination = True
    page_query_param = 'page'
    page_size_query_param = 'size'
    default_page_size = 10

    filter_backends = [filters.DjangoFilterBackend]

    def page_num(self, request):
        page = request.query_params.get(self.page_query_param)
        if not page:
            page = 1
        return max(int(page), 1)

    def page_size(self, request):
        size = request.query_params.get(self.page_size_query_param)
        return int(size) if size else self.default_page_size

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        if not self.enable_pagination:
            serializer = self.get_serializer(queryset, many=True)
            return self.ok_resp(self.CODE_OK, data={
                'items': serializer.data
            })

        page_num = self.page_num(request)
        page_size = self.page_size(request)
        paginator = Paginator(queryset, page_size)
        page = paginator.get_page(page_num)
        serializer = self.get_serializer(page.object_list, many=True)
        return self.ok_resp(self.CODE_OK, data={
            'items': serializer.data,
            'page': page_num,
            'page_size': page_size,
            'total_page': paginator.num_pages,
            'total_count': paginator.count
        })


class CreateModelMixin(BaseAPIViewMixin):
    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return self.ok_resp(self.CODE_OK, data={'item': serializer.data})
        else:
            return self.ok_resp(self.CODE_INVALID_PARAMS, data={'errors': serializer.errors})


class UpdateModelMixin(BaseAPIViewMixin):
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return self.ok_resp(self.CODE_RESOURCE_NOT_FOUND)
        data = request.data
        serializer = self.get_serializer(instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return self.ok_resp(self.CODE_OK, data={'item': serializer.data})
        else:
            return self.ok_resp(self.CODE_INVALID_PARAMS, data={'errors': serializer.errors})


class DestroyModelMixin(BaseAPIViewMixin):
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:
            instance.delete()
        return self.ok_resp(self.CODE_OK)


class BaseRestfulMixin(RetrieveModelMixin,
                       ListModelMixin,
                       CreateModelMixin,
                       UpdateModelMixin,
                       DestroyModelMixin):
    http_method_names = ['get', 'post', 'put', 'delete']

    serializer_class = None

    def get(self, request, pk=None):
        if not pk:
            return self.list(request)
        return self.retrieve(request)

    def post(self, request):
        return self.create(request)

    def put(self, request, pk):
        return self.update(request)

    def delete(self, request, pk):
        return self.destroy(request)

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            return None


class BaseDownloadMixin:
    http_method_names = ['get']
    filter_backends = [filters.DjangoFilterBackend]
    file_name = ''

    def get(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        data = self.download(queryset)
        return FileResponse(data, as_attachment=True, filename=self.file_name)

    def download(self, queryset):
        raise NotImplementedError()


class BaseExcelComposeMixin:
    """
    sheets = (
        {
            'title': '样例',
            'filter_queryset_method': None,
            'fields_map': (
                ('编号', 'id' # 也可以是一个callable，传进一个model object ),
            ),
        }
    )
    """
    sheets = ()

    def create_excel(self, queryset):
        wb = Workbook()
        for index, sheet_info in enumerate(self.sheets):
            if sheet_info.get('filter_queryset_method') is not None:
                queryset = getattr(self, sheet_info.get('filter_queryset_method'))(queryset)
            sheet = wb.create_sheet() if index > 0 else wb.active
            self.write_to_sheet(sheet_info.get('title'), sheet, queryset, sheet_info['fields_map'])
        tmp_file = NamedTemporaryFile()
        wb.save(tmp_file.name)
        tmp_file.seek(0)
        return tmp_file

    def write_to_sheet(self, title, sheet, queryset, fields_map):
        sheet.title = title
        header = ['序号'] + [f_map[0] for f_map in fields_map]
        sheet.append(header)

        def _get_nested_attr(obj, attr):
            if not attr:
                return '-'
            for name in attr.split('.'):
                obj = getattr(obj, name)
                if not obj:
                    return '-'
            return obj

        for index, q in enumerate(queryset):
            attr_names = [f_map[1] for f_map in fields_map]
            row = [index + 1] + [
                attr(q) if callable(attr) else _get_nested_attr(q, attr)
                for attr in attr_names
            ]
            sheet.append(row)
        return sheet
