#include "py/runtime.h"
#include "mpfile.h"
#include "fb.h"
#include "polygon.h"

const char* s_index_out_of_range = "Index out of range";

#define _swap_int16_t(a, b) { int16_t t = a; a = b; b = t; }
#define _swap_bytes(val) ((((val) >> 8) & 0x00FF) | (((val) << 8) & 0xFF00))
#define ABS(N) (((N) < 0) ? (-(N)) : (N))

static void st7789_FB_print(const mp_print_t *print, mp_obj_t self_in, mp_print_kind_t kind) {
    (void)kind;
    st7789_FB_obj_t *self = MP_OBJ_TO_PTR(self_in);
    mp_printf(print, "<FB width=%u, height=%u>", self->width, self->height);
}


static mp_obj_t st7789_FB_width(mp_obj_t self_in){
    st7789_FB_obj_t* self = MP_OBJ_TO_PTR(self_in);
    return mp_obj_new_int(self->width);
}


static MP_DEFINE_CONST_FUN_OBJ_1(st7789_FB_width_obj, st7789_FB_width);


static mp_obj_t st7789_FB_height(mp_obj_t self_in){
    st7789_FB_obj_t* self = MP_OBJ_TO_PTR(self_in);
    return mp_obj_new_int(self->height);
}


static MP_DEFINE_CONST_FUN_OBJ_1(st7789_FB_height_obj, st7789_FB_height);


static void FBSetWindow(st7789_FB_obj_t *fb, uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1){
    if (x0 > x1 || y0 > y1)
        return;
    if (x0 >= fb->width)
        x0 = fb->width - 1;
    if (y0 >= fb->height)
        y0 = fb->height - 1;
    if (x1 >= fb->width)
        x1 = fb->width - 1;
    if (y1 >= fb->height)
        y1 = fb->height - 1; 
    fb->wx0 = x0;
    fb->wy0 = y0;
    fb->wx1 = x1;
    fb->wy1 = y1;
}


static mp_obj_t st7789_FB_set_window(size_t n_args, const mp_obj_t *args){
    st7789_FB_obj_t *self = MP_OBJ_TO_PTR(args[0]);
    if (self->width == 0 || self->height == 0)
        return mp_const_none;
    mp_int_t x0 = mp_obj_get_int(args[1]);
    mp_int_t y0 = mp_obj_get_int(args[2]);
    mp_int_t x1 = mp_obj_get_int(args[3]);
    mp_int_t y1 = mp_obj_get_int(args[4]);
    FBSetWindow(self, x0, y0, x1, y1);    
    return mp_const_none;
}


static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(st7789_FB_set_window_obj, 5, 5, st7789_FB_set_window);


static mp_obj_t st7789_FB_fill(mp_obj_t self_in, mp_obj_t c_in){
    st7789_FB_obj_t* self = MP_OBJ_TO_PTR(self_in);
    uint16_t c = mp_obj_get_int(c_in);
    c = _swap_bytes(c);

    for(uint32_t i=0;i<self->len;++i)
        self->buffer[i]=c;

    return mp_const_none;
}


static MP_DEFINE_CONST_FUN_OBJ_2(st7789_FB_fill_obj, st7789_FB_fill);


static mp_obj_t st7789_FB_get_pixel(mp_obj_t self_in, mp_obj_t x_in, mp_obj_t y_in){
    st7789_FB_obj_t* self = MP_OBJ_TO_PTR(self_in);
    int16_t x = mp_obj_get_int(x_in);
    int16_t y = mp_obj_get_int(y_in);

    if(x < 0 || y < 0 || x >= self->width || y >= self->height){
        mp_raise_ValueError(MP_ERROR_TEXT(s_index_out_of_range));
        return mp_const_none;
    }

    uint16_t c = self->buffer[y * self->width + x];
    return mp_obj_new_int(_swap_bytes(c));
}

static MP_DEFINE_CONST_FUN_OBJ_3(st7789_FB_get_pixel_obj, st7789_FB_get_pixel);


static void fb_draw_pixel(st7789_FB_obj_t* fb, int16_t x, int16_t y, uint16_t c) {
    if(x < fb->wx0 || y < fb->wy0 || x > fb->wx1 || y > fb->wy1)
        return;
    fb->buffer[y * fb->width + x] = c;
}


static mp_obj_t st7789_FB_set_pixel(size_t n_args, const mp_obj_t *args){
    st7789_FB_obj_t* self = MP_OBJ_TO_PTR(args[0]);
    int16_t x = mp_obj_get_int(args[1]);
    int16_t y = mp_obj_get_int(args[2]);
    uint16_t c = mp_obj_get_int(args[3]);
    c = _swap_bytes(c);

    fb_draw_pixel(self, x, y, c);

    return mp_const_none;
}


static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(st7789_FB_set_pixel_obj, 4, 4, st7789_FB_set_pixel);


static void vline(st7789_FB_obj_t* fb, int16_t x, int16_t y, int16_t l, uint16_t c){
    if (fb->width == 0 || fb->height == 0 || x < fb->wx0 || x > fb->wx1 || l <= 0)
        return;
    int16_t y1 = y + l - 1;
    if(y < fb->wy0)
        y = fb->wy0;
    if(y1 > fb->wy1)
        y1 = fb->wy1;
    for (int16_t i = y;i <= y1;++i)
        fb->buffer[i * fb->width + x] = c;
}


static mp_obj_t st7789_FB_vline(size_t n_args, const mp_obj_t *args){
    st7789_FB_obj_t* self = MP_OBJ_TO_PTR(args[0]);
    int16_t x = mp_obj_get_int(args[1]);
    int16_t y = mp_obj_get_int(args[2]);
    int16_t l = mp_obj_get_int(args[3]);
    uint16_t c = mp_obj_get_int(args[4]);
    c = _swap_bytes(c);
    
    vline(self,x,y,l,c);

    return mp_const_none;
}


static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(st7789_FB_vline_obj, 5, 5, st7789_FB_vline);


static void hline(void* fb_in, int16_t x, int16_t y, int16_t l, uint16_t c){
    st7789_FB_obj_t* fb = (st7789_FB_obj_t*)fb_in;
    if (fb->width == 0 || fb->height == 0 || y < fb->wy0 || y > fb->wy1 || l <= 0)
        return;
    int16_t x1 = x + l - 1;
    if(x < fb->wx0)
        x = fb->wx0;
    if(x1 > fb->wx1)
        x1 = fb->wx1;
    uint32_t base = y * fb->width;
    for (int16_t i = x;i <= x1;++i)
        fb->buffer[base + i] = c;
}


static mp_obj_t st7789_FB_hline(size_t n_args, const mp_obj_t *args){
    st7789_FB_obj_t* self = MP_OBJ_TO_PTR(args[0]);
    int16_t x = mp_obj_get_int(args[1]);
    int16_t y = mp_obj_get_int(args[2]);
    int16_t l = mp_obj_get_int(args[3]);
    uint16_t c = mp_obj_get_int(args[4]);
    c = _swap_bytes(c);
    
    hline(self,x,y,l,c);

    return mp_const_none;
}


static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(st7789_FB_hline_obj, 5, 5, st7789_FB_hline);


static void line(st7789_FB_obj_t* fb, int16_t x0, int16_t y0, int16_t x1, int16_t y1, uint16_t c){
    bool steep = ABS(y1 - y0) > ABS(x1 - x0);
    if (steep) {
        _swap_int16_t(x0, y0);
        _swap_int16_t(x1, y1);
    }

    if (x0 > x1) {
        _swap_int16_t(x0, x1);
        _swap_int16_t(y0, y1);
    }

    int16_t dx = x1 - x0, dy = ABS(y1 - y0);
    int16_t err = dx >> 1, ystep = -1, xs = x0, dlen = 0;

    if (y0 < y1)
        ystep = 1;

    // Split into steep and not steep for FastH/V separation
    if (steep) {
        for (; x0 <= x1; x0++) {
            ++dlen;
            err -= dy;
            if (err < 0) {
                err += dx;
                if (dlen == 1)
                    fb_draw_pixel(fb, y0, xs, c);
                else
                    vline(fb, y0, xs, dlen, c);
                dlen = 0;
                y0 += ystep;
                xs = x0 + 1;
            }
        }
        if (dlen)
            vline(fb, y0, xs, dlen, c);
    } 
    else {
        for (; x0 <= x1; x0++) {
            ++dlen;
            err -= dy;
            if (err < 0) {
                err += dx;
                if (dlen == 1)
                    fb_draw_pixel(fb, xs, y0, c);
                else
                    hline(fb, xs, y0, dlen, c);
                dlen = 0;
                y0 += ystep;
                xs = x0 + 1;
            }
        }
        if (dlen)
            hline(fb, xs, y0, dlen, c);
    }
}


static mp_obj_t st7789_FB_line(size_t n_args, const mp_obj_t *args){
    st7789_FB_obj_t* self = MP_OBJ_TO_PTR(args[0]);
    int16_t x0 = mp_obj_get_int(args[1]);
    int16_t y0 = mp_obj_get_int(args[2]);
    int16_t x1 = mp_obj_get_int(args[3]);
    int16_t y1 = mp_obj_get_int(args[4]);
    uint16_t c = mp_obj_get_int(args[5]);
    c = _swap_bytes(c);
    
    line(self, x0, y0, x1, y1, c);

    return mp_const_none;
}


static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(st7789_FB_line_obj, 6, 6, st7789_FB_line);


static mp_obj_t st7789_FB_rect(size_t n_args, const mp_obj_t *args){
    st7789_FB_obj_t* self = MP_OBJ_TO_PTR(args[0]);
    int16_t x = mp_obj_get_int(args[1]);
    int16_t y = mp_obj_get_int(args[2]);
    int16_t w = mp_obj_get_int(args[3]);
    int16_t h = mp_obj_get_int(args[4]);
    uint16_t c = mp_obj_get_int(args[5]);
    c = _swap_bytes(c);

    hline(self, x, y, w, c);
    vline(self, x, y, h, c);
    hline(self, x, y + h - 1, w, c);
    vline(self, x + w - 1, y, h, c);

    return mp_const_none;
}


static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(st7789_FB_rect_obj, 6, 6, st7789_FB_rect);


static mp_obj_t st7789_FB_fill_rect(size_t n_args, const mp_obj_t *args){
    st7789_FB_obj_t* self = MP_OBJ_TO_PTR(args[0]);
    if (self->width <= 0 || self->height <= 0)
        return mp_const_none;
    int16_t x = mp_obj_get_int(args[1]);
    int16_t y = mp_obj_get_int(args[2]);
    int16_t w = mp_obj_get_int(args[3]);
    int16_t h = mp_obj_get_int(args[4]);
    if(w < 0 || h < 0)
        return mp_const_none;
    uint16_t c = mp_obj_get_int(args[5]);
    c = _swap_bytes(c);

    int16_t x1 = x + w - 1;
    int16_t y1 = y + h - 1;
    
    if(x < self->wx0)
        x = self->wx0;
    if(x1 > self->wx1)
        x1 = self->wx1;
    if(y < self->wy0)
        y = self->wy0;
    if(y1 > self->wy1)
        y1 = self->wy1;

    int32_t base;
    
    for(int16_t j = y;j <= y1;++j){
        base = j * self->width;
        for(int16_t i = x;i <= x1;++i)
            self->buffer[base + i] = c;
    }
    
    return mp_const_none;
}


static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(st7789_FB_fill_rect_obj, 6, 6, st7789_FB_fill_rect);


// Circle/Fill_Circle by https://github.com/c-logic
// https://github.com/russhughes/st7789_mpy/pull/46
// https://github.com/c-logic/st7789_mpy.git patch-1

static mp_obj_t st7789_FB_circle(size_t n_args, const mp_obj_t *args) {
    st7789_FB_obj_t *self = MP_OBJ_TO_PTR(args[0]);
    mp_int_t xm = mp_obj_get_int(args[1]);
    mp_int_t ym = mp_obj_get_int(args[2]);
    mp_int_t r = mp_obj_get_int(args[3]);
    mp_int_t color = mp_obj_get_int(args[4]);

    mp_int_t f = 1 - r;
    mp_int_t ddF_x = 1;
    mp_int_t ddF_y = -2 * r;
    mp_int_t x = 0;
    mp_int_t y = r;

    fb_draw_pixel(self, xm, ym + r, color);
    fb_draw_pixel(self, xm, ym - r, color);
    fb_draw_pixel(self, xm + r, ym, color);
    fb_draw_pixel(self, xm - r, ym, color);
    while (x < y) {
        if (f >= 0) {
            y -= 1;
            ddF_y += 2;
            f += ddF_y;
        }
        x += 1;
        ddF_x += 2;
        f += ddF_x;
        fb_draw_pixel(self, xm + x, ym + y, color);
        fb_draw_pixel(self, xm - x, ym + y, color);
        fb_draw_pixel(self, xm + x, ym - y, color);
        fb_draw_pixel(self, xm - x, ym - y, color);
        fb_draw_pixel(self, xm + y, ym + x, color);
        fb_draw_pixel(self, xm - y, ym + x, color);
        fb_draw_pixel(self, xm + y, ym - x, color);
        fb_draw_pixel(self, xm - y, ym - x, color);
    }
    return mp_const_none;
}

static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(st7789_FB_circle_obj, 5, 5, st7789_FB_circle);


static mp_obj_t st7789_FB_fill_circle(size_t n_args, const mp_obj_t *args) {
    st7789_FB_obj_t *self = MP_OBJ_TO_PTR(args[0]);
    mp_int_t ym = mp_obj_get_int(args[1]);
    mp_int_t xm = mp_obj_get_int(args[2]);
    mp_int_t r = mp_obj_get_int(args[3]);
    mp_int_t c = mp_obj_get_int(args[4]);
    c = _swap_bytes(c);

    mp_int_t f = 1 - r;
    mp_int_t ddF_x = 1;
    mp_int_t ddF_y = -2 * r;
    mp_int_t x = 0;
    mp_int_t y = r;

    hline(self, ym - y, xm, 2 * y + 1, c);

    while (x < y) {
        if (f >= 0) {
            y -= 1;
            ddF_y += 2;
            f += ddF_y;
        }
        x += 1;
        ddF_x += 2;
        f += ddF_x;
        hline(self, ym - y, xm + x, 2 * y + 1, c);
        hline(self, ym - x, xm + y, 2 * x + 1, c);
        hline(self, ym - y, xm - x, 2 * y + 1, c);
        hline(self, ym - x, xm - y, 2 * x + 1, c);
    }
    return mp_const_none;
}


static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(st7789_FB_fill_circle_obj, 5, 5, st7789_FB_fill_circle);


static mp_obj_t st7789_FB_polygon(size_t n_args, const mp_obj_t *args) {
    st7789_FB_obj_t *self = MP_OBJ_TO_PTR(args[0]);

    size_t poly_len;
    mp_obj_t *polygon;
    mp_obj_get_array(args[1], &poly_len, &polygon);

    self->work = NULL;

    if (poly_len > 0) {
        mp_int_t x = mp_obj_get_int(args[2]);
        mp_int_t y = mp_obj_get_int(args[3]);
        mp_int_t color = mp_obj_get_int(args[4]);

        mp_float_t angle = 0.0f;
        if (n_args > 5 && mp_obj_is_float(args[5])) {
            angle = mp_obj_float_get(args[5]);
        }

        mp_int_t cx = 0;
        mp_int_t cy = 0;

        if (n_args > 6) {
            cx = mp_obj_get_int(args[6]);
            cy = mp_obj_get_int(args[7]);
        }

        self->work = m_malloc(poly_len * sizeof(Point));
        if (self->work) {
            Point *point = (Point *)self->work;

            for (int idx = 0; idx < poly_len; idx++) {
                size_t point_from_poly_len;
                mp_obj_t *point_from_poly;
                mp_obj_get_array(polygon[idx], &point_from_poly_len, &point_from_poly);
                if (point_from_poly_len < 2) {
                    mp_raise_msg(&mp_type_RuntimeError, MP_ERROR_TEXT("Polygon data error"));
                }

                mp_int_t px = mp_obj_get_int(point_from_poly[0]);
                mp_int_t py = mp_obj_get_int(point_from_poly[1]);
                point[idx].x = px;
                point[idx].y = py;
            }

            Point center;
            center.x = cx;
            center.y = cy;

            Polygon polygon;
            polygon.length = poly_len;
            polygon.points = self->work;

            if (angle > 0) {
                RotatePolygon(&polygon, center, angle);
            }

            for (int idx = 1; idx < poly_len; idx++) {
                line(
                    self,
                    (int)point[idx - 1].x + x,
                    (int)point[idx - 1].y + y,
                    (int)point[idx].x + x,
                    (int)point[idx].y + y, color);
            }

            m_free(self->work);
            self->work = NULL;
        } else {
            mp_raise_msg(&mp_type_RuntimeError, MP_ERROR_TEXT("Polygon data error"));
        }
    } else {
        mp_raise_msg(&mp_type_RuntimeError, MP_ERROR_TEXT("Polygon data error"));
    }

    return mp_const_none;
}

static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(st7789_FB_polygon_obj, 4, 8, st7789_FB_polygon);

//
//  filled convex polygon
//

static mp_obj_t st7789_FB_fill_polygon(size_t n_args, const mp_obj_t *args) {
    st7789_FB_obj_t *self = MP_OBJ_TO_PTR(args[0]);

    size_t poly_len;
    mp_obj_t *polygon;
    mp_obj_get_array(args[1], &poly_len, &polygon);

    self->work = NULL;

    if (poly_len > 0) {
        mp_int_t x = mp_obj_get_int(args[2]);
        mp_int_t y = mp_obj_get_int(args[3]);
        mp_int_t color = mp_obj_get_int(args[4]);

        mp_float_t angle = 0.0f;
        if (n_args > 5) {
            angle = mp_obj_float_get(args[5]);
        }

        mp_int_t cx = 0;
        mp_int_t cy = 0;

        if (n_args > 6) {
            cx = mp_obj_get_int(args[6]);
            cy = mp_obj_get_int(args[7]);
        }

        self->work = m_malloc(poly_len * sizeof(Point));
        if (self->work) {
            Point *point = (Point *)self->work;

            for (int idx = 0; idx < poly_len; idx++) {
                size_t point_from_poly_len;
                mp_obj_t *point_from_poly;
                mp_obj_get_array(polygon[idx], &point_from_poly_len, &point_from_poly);
                if (point_from_poly_len < 2) {
                    mp_raise_msg(&mp_type_RuntimeError, MP_ERROR_TEXT("Polygon data error"));
                }

                point[idx].x = mp_obj_get_int(point_from_poly[0]);
                point[idx].y = mp_obj_get_int(point_from_poly[1]);
            }

            Point center = {cx, cy};
            Polygon polygon = {poly_len, self->work};

            if (angle != 0) {
                RotatePolygon(&polygon, center, angle);
            }

            Point location = {x, y};
            PolygonFill(self, hline, &polygon, location, color);

            m_free(self->work);
            self->work = NULL;
        } else {
            mp_raise_msg(&mp_type_RuntimeError, MP_ERROR_TEXT("Polygon data error"));
        }

    } else {
        mp_raise_msg(&mp_type_RuntimeError, MP_ERROR_TEXT("Polygon data error"));
    }

    return mp_const_none;
}


static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(st7789_FB_fill_polygon_obj, 4, 8, st7789_FB_fill_polygon);


static mp_obj_t st7789_FB_text(size_t n_args, const mp_obj_t *args) {
    st7789_FB_obj_t *self = MP_OBJ_TO_PTR(args[0]);
    uint8_t single_char_s;
    const uint8_t *source = NULL;
    size_t source_len = 0;

    // extract arguments
    mp_obj_module_t *font = MP_OBJ_TO_PTR(args[1]);

    if (mp_obj_is_int(args[2])) {
        mp_int_t c = mp_obj_get_int(args[2]);
        single_char_s = (c & 0xff);
        source = &single_char_s;
        source_len = 1;
    } else if (mp_obj_is_str(args[2])) {
        source = (uint8_t *) mp_obj_str_get_str(args[2]);
        source_len = strlen((char *)source);
    } else if (mp_obj_is_type(args[2], &mp_type_bytes)) {
        mp_obj_t text_data_buff = args[2];
        mp_buffer_info_t text_bufinfo;
        mp_get_buffer_raise(text_data_buff, &text_bufinfo, MP_BUFFER_READ);
        source = text_bufinfo.buf;
        source_len = text_bufinfo.len;
    } else {
        mp_raise_TypeError(MP_ERROR_TEXT("text requires either int, str or bytes."));
        return mp_const_none;
    }

    mp_int_t x0 = mp_obj_get_int(args[3]);
    mp_int_t y0 = mp_obj_get_int(args[4]);

    mp_obj_dict_t *dict = MP_OBJ_TO_PTR(font->globals);
    const uint8_t width = mp_obj_get_int(mp_obj_dict_get(dict, MP_OBJ_NEW_QSTR(MP_QSTR_WIDTH)));
    const uint8_t height = mp_obj_get_int(mp_obj_dict_get(dict, MP_OBJ_NEW_QSTR(MP_QSTR_HEIGHT)));
    const uint8_t first = mp_obj_get_int(mp_obj_dict_get(dict, MP_OBJ_NEW_QSTR(MP_QSTR_FIRST)));
    const uint8_t last = mp_obj_get_int(mp_obj_dict_get(dict, MP_OBJ_NEW_QSTR(MP_QSTR_LAST)));

    mp_obj_t font_data_buff = mp_obj_dict_get(dict, MP_OBJ_NEW_QSTR(MP_QSTR_FONT));
    mp_buffer_info_t bufinfo;
    mp_get_buffer_raise(font_data_buff, &bufinfo, MP_BUFFER_READ);
    const uint8_t *font_data = bufinfo.buf;

    mp_int_t fg_color;
    bool has_bg = false;
    mp_int_t bg_color;

    if (n_args > 5)
        fg_color = _swap_bytes(mp_obj_get_int(args[5]));
    else
        fg_color = _swap_bytes(0xFFFF);

    if (n_args > 6){
        has_bg = true;
        bg_color = _swap_bytes(mp_obj_get_int(args[6]));
    }

    uint8_t wide = width / 8;

    uint8_t chr;
    while (source_len--) {
        chr = *source++;
        if (chr >= first && chr <= last) {
            uint16_t buf_idx = 0;
            uint16_t chr_idx = (chr - first) * (height * wide);
            for (uint8_t line = 0; line < height; line++) {
                for (uint8_t line_byte = 0; line_byte < wide; line_byte++) {
                    uint8_t chr_data = font_data[chr_idx];
                    for (uint8_t bit = 8; bit; bit--) {
                        if (chr_data >> (bit - 1) & 1)
                            fb_draw_pixel(self, x0 + line_byte * 8 + (8 - bit), y0 + line, fg_color);
                        else if(has_bg)
                            fb_draw_pixel(self, x0 + line_byte * 8 + (8 - bit), y0 + line, bg_color);
                        buf_idx++;
                    }
                    chr_idx++;
                }
            }
        }
        x0 += width;
    }
    return mp_const_none;
}


static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(st7789_FB_text_obj, 5, 7, st7789_FB_text);


static mp_obj_t st7789_FB___del__(mp_obj_t self_in){
    st7789_FB_obj_t* self = MP_OBJ_TO_PTR(self_in);
    m_free(self->buffer);
    return mp_const_none;
}

static MP_DEFINE_CONST_FUN_OBJ_1(st7789_FB___del___obj, st7789_FB___del__);

static const mp_rom_map_elem_t st7789_FB_locals_dict_table[] = {
    {MP_ROM_QSTR(MP_QSTR_set_window), MP_ROM_PTR(&st7789_FB_set_window_obj)},
    {MP_ROM_QSTR(MP_QSTR_width), MP_ROM_PTR(&st7789_FB_width_obj)},
    {MP_ROM_QSTR(MP_QSTR_height), MP_ROM_PTR(&st7789_FB_height_obj)},
    {MP_ROM_QSTR(MP_QSTR_fill), MP_ROM_PTR(&st7789_FB_fill_obj)},
    {MP_ROM_QSTR(MP_QSTR_get_pixel), MP_ROM_PTR(&st7789_FB_get_pixel_obj)},
    {MP_ROM_QSTR(MP_QSTR_set_pixel), MP_ROM_PTR(&st7789_FB_set_pixel_obj)},
    {MP_ROM_QSTR(MP_QSTR_vline), MP_ROM_PTR(&st7789_FB_vline_obj)},
    {MP_ROM_QSTR(MP_QSTR_hline), MP_ROM_PTR(&st7789_FB_hline_obj)},
    {MP_ROM_QSTR(MP_QSTR_line), MP_ROM_PTR(&st7789_FB_line_obj)},
    {MP_ROM_QSTR(MP_QSTR_rect), MP_ROM_PTR(&st7789_FB_rect_obj)},
    {MP_ROM_QSTR(MP_QSTR_fill_rect), MP_ROM_PTR(&st7789_FB_fill_rect_obj)},
    {MP_ROM_QSTR(MP_QSTR_circle), MP_ROM_PTR(&st7789_FB_circle_obj)},
    {MP_ROM_QSTR(MP_QSTR_fill_circle), MP_ROM_PTR(&st7789_FB_fill_circle_obj)},
    {MP_ROM_QSTR(MP_QSTR_polygon), MP_ROM_PTR(&st7789_FB_polygon_obj)},
    {MP_ROM_QSTR(MP_QSTR_fill_polygon), MP_ROM_PTR(&st7789_FB_fill_polygon_obj)},
    {MP_ROM_QSTR(MP_QSTR_text), MP_ROM_PTR(&st7789_FB_text_obj)},
    {MP_ROM_QSTR(MP_QSTR___del__), MP_ROM_PTR(&st7789_FB___del___obj)},
};
static MP_DEFINE_CONST_DICT(st7789_FB_locals_dict, st7789_FB_locals_dict_table);
/* methods end */

mp_obj_t st7789_FB_make_new(const mp_obj_type_t *type,
    size_t n_args,
    size_t n_kw,
    const mp_obj_t *all_args) {
    static const mp_arg_t allowed_args[] = {
        {MP_QSTR_width, MP_ARG_INT | MP_ARG_REQUIRED, {.u_int = 0}},
        {MP_QSTR_height, MP_ARG_INT | MP_ARG_REQUIRED, {.u_int = 0}},
    };
    mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
    mp_arg_parse_all_kw_array(n_args, n_kw, all_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);

    // create new object
    st7789_FB_obj_t *self = m_malloc_with_finaliser(sizeof(st7789_FB_obj_t));
    self->base.type = &st7789_FB_type;

    // set parameters
    self->width = args[0].u_int;
    self->height = args[1].u_int;
    self->wx0 = 0;
    self->wy0 = 0;
    self->wx1 = self->width > 0 ? self->width - 1 : 0;
    self->wy1 = self->height > 0 ? self->height - 1 : 0;
    self->len = self->width * self->height;

    if (self->width > 0 && self->height > 0)
        self->buffer = m_new(uint16_t, self->width * self->height);

    return MP_OBJ_FROM_PTR(self);
}

#ifdef MP_OBJ_TYPE_GET_SLOT

MP_DEFINE_CONST_OBJ_TYPE(
    st7789_FB_type,
    MP_QSTR_FB,
    MP_TYPE_FLAG_NONE,
    print, st7789_FB_print,
    make_new, st7789_FB_make_new,
    locals_dict, (mp_obj_dict_t *)&st7789_FB_locals_dict);

#else

const mp_obj_type_t st7789_FB_type = {
    {&mp_type_type},
    .name = MP_QSTR_FB,
    .print = st7789_FB_print,
    .make_new = st7789_FB_make_new,
    .locals_dict = (mp_obj_dict_t *)&st7789_FB_locals_dict,
};


#endif