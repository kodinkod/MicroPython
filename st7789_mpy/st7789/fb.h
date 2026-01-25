#ifndef __FB_H__
#define __FB_H__

#ifdef __cplusplus
extern "C" {
#endif


typedef struct st7789_FB_obj_t {
    mp_obj_base_t base;
    uint16_t width;
    uint16_t height;
    uint16_t wx0;
    uint16_t wy0;
    uint16_t wx1;
    uint16_t wy1;
    uint16_t* buffer;
    uint32_t len;
    void *work; 
} st7789_FB_obj_t;


extern const mp_obj_type_t st7789_FB_type;

#ifdef  __cplusplus
}
#endif /*  __cplusplus */

#endif  /*  __FB_H__ */