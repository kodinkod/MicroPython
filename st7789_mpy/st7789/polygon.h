#ifndef __POLYGON_H__
#define __POLYGON_H__

#ifdef __cplusplus
extern "C" {
#endif

#define MAX_POLY_CORNERS 32

typedef struct _Point {
    mp_float_t x;
    mp_float_t y;
} Point;

typedef struct _Polygon {
    int length;
    Point *points;
} Polygon;

typedef void (*hline_f)(void*, int16_t, int16_t, int16_t, uint16_t);

extern void RotatePolygon(Polygon *polygon, Point center, mp_float_t angle);
extern void PolygonFill(void *self, hline_f hlf, Polygon *polygon, Point location, uint16_t color);

#ifdef  __cplusplus
}
#endif /*  __cplusplus */

#endif  /*  __POLYGON_H__ */