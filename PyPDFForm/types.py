# -*- coding: utf-8 -*-


class PdfWrapperList(list):
    def __getitem__(self, key: any) -> list | any:
        if isinstance(key, slice):
            result = None
            l = super().__getitem__(key)
            for each in l:
                if not result:
                    result = each
                else:
                    result += each

            return result if result else []
        else:
            return super().__getitem__(key)
