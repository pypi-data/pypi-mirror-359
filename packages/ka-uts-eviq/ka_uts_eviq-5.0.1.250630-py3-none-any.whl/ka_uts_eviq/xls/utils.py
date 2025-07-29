"""
This module provides utility classes for the management of OmniTracker
EcoVadis NHRR (Nachhaltigkeits Risiko Rating) processing for Department UMH
"""
from __future__ import annotations
from typing import Any, TypeAlias

import pandas as pd
import numpy as np

from ka_uts_aod.aod import AoD
from ka_uts_dic.dic import Dic
from ka_uts_dic.doa import DoA
from ka_uts_dic.doaod import DoAoD
from ka_uts_dfr.pddf import PdDf
from ka_uts_log.log import Log

from .cfg import Cfg
from .verify import EvinVfyAdm, EvinVfyDel

TyPdDf: TypeAlias = pd.DataFrame

TyArr = list[Any]
TyAoStr = list[str]
TyBool = bool
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyDoAoA = dict[Any, TyAoA]
TyDoAoD = dict[Any, TyAoD]
TyDoB = dict[Any, bool]
TyAoD_DoAoD = TyAoD | TyDoAoD
TyPath = str
TyStr = str
TyTup = tuple[Any]
TyTask = Any
TyDoPdDf = dict[Any, TyPdDf]
TyPdDf_DoPdDf = TyPdDf | TyDoPdDf
TyToAoDDoAoD = tuple[TyAoD, TyDoAoD]

TnDic = None | TyDic
TnAoD = None | TyAoD
TnDoAoA = None | TyDoAoA
TnDoAoD = None | TyDoAoD
TnPdDf = None | TyPdDf
TnStr = None | str

CfgUtils = Cfg.Utils


class Evup:
    """
    EcoVadis Upload class
    """
    kwargs_wb = dict(dtype=str, keep_default_na=False, engine='calamine')

    @classmethod
    def sh_aod_evup_adm(
            cls,
            aod_evin: TnAoD,
            pddf_evex: TnPdDf,
            doaod_vfy: TyDoAoD,
            kwargs: TyDic
    ) -> TyAoD:
        # _aod_evin: TyAoD = EvinVfyAdm.vfy_aod_evin(aod_evin, doaod_vfy, kwargs)

        _sw_adm_use_evex: TyBool = kwargs.get('sw_adm_use_evex', False)
        _doaod_evup_adm = EvinEvex.join_adm(aod_evin, pddf_evex, _sw_adm_use_evex)
        if _sw_adm_use_evex:
            _aod = DoAoD.union_by_keys(_doaod_evup_adm, ['new', 'ch_y'])
        else:
            _aod = DoAoD.union(_doaod_evup_adm)

        _aod = EvinVfyAdm.vfy_aod_evin(_aod, doaod_vfy, kwargs)
        return _aod

    @staticmethod
    def sh_aod_evup_del_use_evex(
            aod_evin_del: TnAoD,
            pddf_evin_adm: TnPdDf,
            aod_evex: TnAoD,
            pddf_evex: TnPdDf,
            doaod_vfy: TyDoAoD,
            kwargs: TyDic
    ) -> TnAoD:
        _aod_evin_del: TyAoD = EvinVfyDel.vfy_aod_evin(aod_evin_del, doaod_vfy, kwargs)
        _aod_evup_del0: TnAoD = EvexEvin.join_del(aod_evex, pddf_evin_adm)
        _aod_evup_del1: TnAoD = EvinEvex.join_del(_aod_evin_del, pddf_evex)
        return AoD.union(_aod_evup_del0, _aod_evup_del1)

    @staticmethod
    def sh_aod_evup_del(
            aod_evin_del: TnAoD,
            pddf_evin_adm: TnPdDf,
            doaod_vfy: TyDoAoD,
            kwargs: TyDic
    ) -> TnAoD:
        _aod_evin_del: TyAoD = EvinVfyDel.vfy_aod_evin(aod_evin_del, doaod_vfy, kwargs)
        return _aod_evin_del


class Evex:
    """
    EcoVadis Export class
    """
    @staticmethod
    def sh_d_evex(df_evex: TnPdDf) -> TyDic:
        if df_evex is None:
            return {}
        _df_evex = df_evex.replace(to_replace=np.nan, value=None, inplace=False)
        _aod = _df_evex.to_dict(orient='records')
        if len(_aod) == 1:
            d_evex: TyDic = _aod[0]
            return d_evex
        msg = "Evex Dataframe: {F} contains multiple records: {R}"
        Log.error(msg.format(F=df_evex, R=_aod))
        return {}

    @staticmethod
    def sh_d_evup_del_from_dic(d_evex: TnDic) -> TnDic:
        d_evup: TyDic = {}
        if d_evex is None:
            return d_evup
        Dic.set_tgt_with_src_by_d_tgt2src(d_evup, d_evex, CfgUtils.d_del_evup2evex)
        return d_evup

    @classmethod
    def sh_d_evup_del_from_df(cls, df_evex_row: TyPdDf) -> TnDic:
        _d_evex: TnDic = cls.sh_d_evex(df_evex_row)
        return cls.sh_d_evup_del_from_dic(_d_evex)

    @staticmethod
    def map(aod_evex: TnAoD, d_map_evex: TyDic) -> TyAoD:
        aod_evex_new: TyAoD = []
        if not aod_evex:
            return aod_evex_new
        for dic in aod_evex:
            dic_new = {}
            for key, value in dic.items():
                dic_new[key] = d_map_evex.get(value, value)
            aod_evex_new.append(dic_new)
        return aod_evex_new


class Evin:
    """
    EcoVadis input data (from Systems like OmniTracker) class
    """

    @staticmethod
    def sh_d_evup_adm(d_evin: TyDic) -> TyDic:
        d_evup: TyDic = {}
        Dic.set_tgt_with_src(d_evup, CfgUtils.d_evup2const)
        Dic.set_tgt_with_src_by_d_tgt2src(d_evup, d_evin, CfgUtils.d_evup2evin)
        return d_evup

    @classmethod
    def sh_aod_evup_adm(cls, aod_evin) -> TyAoD:
        _aod_evup: TyAoD = []
        for _d_evin in aod_evin:
            _d_evup = Evin.sh_d_evup_adm(_d_evin)
            AoD.append_unique(_aod_evup, _d_evup)
        return _aod_evup

    @classmethod
    def sh_doaod_adm_new(cls, aod_evin) -> TyDoAoD:
        _doaod_evup: TyDoAoD = {}
        for _d_evin in aod_evin:
            _d_evup = cls.sh_d_evup_adm(_d_evin)
            DoA.append_unique_by_key(_doaod_evup, 'new', _d_evup)
        return _doaod_evup


class EvinEvex:
    """
    Check EcoVadis input data (from Systems like OmniTracker) against
    EcoVadis export data
    """
    msg_evex = ("No entries found in Evex dataframe for "
                "Evex key: '{K1}' and Evin value: {V1} and "
                "Evex key: '{K2}' and Evin value: {V2}")
    msg_evin = "Evin Key: '{K}' not found in Evin Dictionary {D}"

    @classmethod
    def query_with_key(
            cls, d_evin: TyDic, df_evex: TnPdDf, evin_key: Any, evin_value_cc: Any
    ) -> TnPdDf:
        if not df_evex:
            return None
        evin_value = Dic.get(d_evin, evin_key)
        if not evin_value:
            Log.debug(cls.msg_evin.format(K=evin_key, D=d_evin))
            return None
        evex_key = CfgUtils.d_evin2evex_keys[evin_key]
        condition = (df_evex[evex_key] == evin_value) & (df_evex[CfgUtils.evex_key_cc] == evin_value_cc)
        df: TnPdDf = df_evex.loc[condition]
        Log.info(cls.msg_evex.format(
            K1=evex_key, V1=evin_value, K2=CfgUtils.evex_key_cc, V2=evin_value_cc))
        return df

    @classmethod
    def query_with_keys(cls, d_evin: TyDic, df_evex: TnPdDf) -> TnPdDf:
        evin_value_cc = d_evin.get(CfgUtils.evin_key_cc)
        if not evin_value_cc:
            Log.error(cls.msg_evin.format(K=CfgUtils.evin_key_cc, D=d_evin))
            return None
        for evin_key in CfgUtils.a_evin_key:
            df = cls.query_with_key(d_evin, df_evex, evin_key, evin_value_cc)
            if df is not None:
                return df
        return None

    @classmethod
    def query(cls, d_evin: TyDic, df_evex: TnPdDf) -> TyDic:
        _df: TnPdDf = PdDf.query_with_key(
            df_evex, d_evin,
            dic_key=CfgUtils.evin_key_objectid, d_key2key=CfgUtils.d_evin2evex_keys)
        if _df is not None:
            return Evex.sh_d_evex(_df)

        _df = PdDf.query_with_key(
            df_evex, d_evin,
            dic_key=CfgUtils.evin_key_duns, d_key2key=CfgUtils.d_evin2evex_keys)
        if _df is not None:
            return Evex.sh_d_evex(_df)

        _df = cls.query_with_keys(d_evin, df_evex)
        return Evex.sh_d_evex(_df)

    @classmethod
    def join_adm(
            cls, aod_evin: TnAoD, df_evex: TnPdDf, sw_adm_use_evex: TyBool
    ) -> TyDoAoD:
        if not aod_evin:
            return {}
        if df_evex is None:
            return Evin.sh_doaod_adm_new(aod_evin)

        _doaod_evup: TyDoAoD = {}
        for _d_evin in aod_evin:
            _df: TnPdDf = PdDf.query_with_key(
                df_evex, _d_evin,
                dic_key=CfgUtils.evin_key_objectid, d_key2key=CfgUtils.d_evin2evex_keys)
            if _df is None:
                _d_evup = Evin.sh_d_evup_adm(_d_evin)
                DoA.append_unique_by_key(_doaod_evup, 'new', _d_evup)
            else:
                _d_evex = Evex.sh_d_evex(_df)
                _change_status, _d_evup = cls.sh_d_evup_adm(
                    _d_evin, _d_evex, sw_adm_use_evex)
                DoA.append_unique_by_key(_doaod_evup, _change_status, _d_evup)
        return _doaod_evup

    @classmethod
    def join_del(
            cls, aod_evin: TnAoD, df_evex: TnPdDf
    ) -> TyAoD:
        _aod_evup: TyAoD = []
        if not aod_evin:
            return _aod_evup

        for _d_evin in aod_evin:
            _df_evex_row: TnPdDf = PdDf.query_with_key(
                    df_evex, _d_evin,
                    dic_key=CfgUtils.evin_key_objectid,
                    d_key2key=CfgUtils.d_evin2evex_keys)
            if _df_evex_row is not None:
                _d_evup_del: TnDic = Evex.sh_d_evup_del_from_df(_df_evex_row)
                if _d_evup_del:
                    AoD.append_unique(_aod_evup, _d_evup_del)
        return _aod_evup

    @staticmethod
    def sh_d_evup_adm(
            d_evin: TyDic, d_evex: TyDic, sw_adm_use_evex: TyBool) -> tuple[str, TyDic]:
        d_evup: TyDic = {}
        Dic.set_tgt_with_src(d_evup, CfgUtils.d_evup2const)

        if sw_adm_use_evex:
            Dic.set_tgt_with_src_by_d_tgt2src(d_evup, d_evex, CfgUtils.d_evup2evex)
            Dic.set_tgt_with_src_by_d_tgt2src(d_evup, d_evin, CfgUtils.d_evup2evin)
            for key_evup, key_evex in CfgUtils.d_evup2evex.items():
                if d_evup[key_evup] != d_evex[key_evex]:
                    return 'ch_y', d_evup
            return 'ch_n', d_evup
        else:
            Dic.set_tgt_with_src_by_d_tgt2src(d_evup, d_evex, CfgUtils.d_evup2evex)
            Dic.set_tgt_with_src_by_d_tgt2src(d_evup, d_evin, CfgUtils.d_evup2evin)
            return '-', d_evup


class EvexEvin:
    """
    Check EcoVadis Export Data against
    EcoVadis input data (from Systems like OmniTracker)
    """
    @classmethod
    def join_del(
            cls, aod_evex: TnAoD, df_evin: TnPdDf
    ) -> TyAoD:
        _aod_evup: TyAoD = []
        if not aod_evex or df_evin is None:
            return _aod_evup
        for _d_evex in aod_evex:
            _df_evin_row: TnPdDf = PdDf.query_with_key(
                df_evin, _d_evex,
                dic_key=CfgUtils.evin_key_objectid, d_key2key=CfgUtils.d_evex2evin_keys)
            if _df_evin_row is None:
                _d_evup = Evex.sh_d_evup_del_from_dic(_d_evex)
                if _d_evup:
                    AoD.append_unique(_aod_evup, _d_evup)
        return _aod_evup
