#include <stdio.h>
#include <stdarg.h>

#include "chipmunk/chipmunk_private.h"

//
// Functions to support efficient batch API
//

typedef enum pmBatchableBodyFields
{
    BODY_ID = 1 << 0,
    POSITION = 1 << 1,
    ANGLE = 1 << 2,
    VELOCITY = 1 << 3,
    ANGULAR_VELOCITY = 1 << 4,
    FORCE = 1 << 5,
    TORQUE = 1 << 6,
} pmBatchableBodyFields;

typedef enum pmBatchableArbiterFields
{
    BODY_A_ID = 1 << 0,
    BODY_B_ID = 1 << 1,
    TOTAL_IMPULSE = 1 << 2,
    TOTAL_KE = 1 << 3,
    IS_FIRST_CONTACT = 1 << 4,
    NORMAL = 1 << 5,

    CONTACT_COUNT = 1 << 6,

    POINT_A_1 = 1 << 7,
    POINT_B_1 = 1 << 8,
    DISTANCE_1 = 1 << 9,

    POINT_A_2 = 1 << 10,
    POINT_B_2 = 1 << 11,
    DISTANCE_2 = 1 << 12,
} pmBatchableArbiterFields;

// typedef struct pmVectArray pmVectArray;
typedef struct pmFloatArray pmFloatArray;
typedef struct pmIntArray pmIntArray;
typedef struct pmBatchedData pmBatchedData;

// struct pmVectArray
// {
//     int num, max;
//     cpVect *arr;
// };

struct pmFloatArray
{
    int num, max;
    cpFloat *arr;
};

struct pmIntArray
{
    int num, max;
    uintptr_t *arr;
};

struct pmBatchedData
{
    pmIntArray *intArray;
    pmFloatArray *floatArray;
    pmBatchableBodyFields fields;
};

pmFloatArray *
pmFloatArrayNew(int size)
{
    pmFloatArray *arr = (pmFloatArray *)cpcalloc(1, sizeof(pmFloatArray));

    arr->num = 0;
    arr->max = (size ? size : 4);
    arr->arr = (cpFloat *)cpcalloc(arr->max, sizeof(cpFloat));

    return arr;
}

void pmFloatArrayFree(pmFloatArray *arr)
{
    if (arr)
    {
        cpfree(arr->arr);
        arr->arr = NULL;

        cpfree(arr);
    }
}

void pmFloatArrayPush(pmFloatArray *arr, cpFloat v)
{
    if (arr->num == (arr->max - 1) || arr->num == arr->max)
    {
        arr->max = 3 * (arr->max + 1) / 2;
        arr->arr = (cpFloat *)cprealloc(arr->arr, arr->max * sizeof(cpFloat));
    }
    arr->arr[arr->num] = v;
    arr->num++;
}

cpFloat
pmFloatArrayPop(pmFloatArray *arr)
{
    cpFloat value = (cpFloat)arr->arr[arr->num];
    arr->num++;	
	return value;
}

void pmFloatArrayPushVect(pmFloatArray *arr, cpVect v)
{
    if (arr->num == (arr->max - 2) || arr->num == (arr->max - 1) || arr->num == arr->max)
    {
        arr->max = 3 * (arr->max + 1) / 2;
        arr->arr = (cpFloat *)cprealloc(arr->arr, arr->max * sizeof(cpFloat));
    }
    arr->arr[arr->num] = v.x;
    arr->arr[arr->num + 1] = v.y;
    arr->num += 2;
}

cpVect
pmFloatArrayPopVect(pmFloatArray *arr)
{
    cpVect value = cpv((cpFloat)arr->arr[arr->num], (cpFloat)arr->arr[arr->num+1]);
	arr->num += 2;			
	return value;
}

pmIntArray *
pmIntArrayNew(int size)
{
    pmIntArray *arr = (pmIntArray *)cpcalloc(1, sizeof(pmIntArray));

    arr->num = 0;
    arr->max = (size ? size : 4);
    arr->arr = (uintptr_t *)cpcalloc(arr->max, sizeof(uintptr_t));

    return arr;
}

void pmIntArrayFree(pmIntArray *arr)
{
    if (arr)
    {
        cpfree(arr->arr);
        arr->arr = NULL;

        cpfree(arr);
    }
}

void pmIntArrayPush(pmIntArray *arr, uintptr_t v)
{
    if (arr->num == (arr->max - 1) || arr->num == arr->max)
    {
        arr->max = 3 * (arr->max + 1) / 2;
        arr->arr = (uintptr_t *)cprealloc(arr->arr, arr->max * sizeof(uintptr_t));
    }
    arr->arr[arr->num] = v;
    arr->num++;
}

uintptr_t
pmIntArrayPop(pmIntArray *arr)
{	
	uintptr_t value = (uintptr_t)arr->arr[arr->num];
	arr->num++;
	return value;
}

void pmSpaceBodyGetIteratorFuncBatched(cpBody *body, void *data)
{
    pmBatchedData *d = (pmBatchedData *)data;

    if (d->fields & BODY_ID)
    {
        pmIntArrayPush(d->intArray, (uintptr_t)cpBodyGetUserData(body));
    }
    if (d->fields & POSITION)
    {
        pmFloatArrayPushVect(d->floatArray, cpBodyGetPosition(body));
    }
    if (d->fields & ANGLE)
    {
        pmFloatArrayPush(d->floatArray, cpBodyGetAngle(body));
    }
    if (d->fields & VELOCITY)
    {
        pmFloatArrayPushVect(d->floatArray, cpBodyGetVelocity(body));
    }
    if (d->fields & ANGULAR_VELOCITY)
    {
        pmFloatArrayPush(d->floatArray, cpBodyGetAngularVelocity(body));
    }
    if (d->fields & FORCE)
    {
        pmFloatArrayPushVect(d->floatArray, cpBodyGetForce(body));
    }
    if (d->fields & TORQUE)
    {
        pmFloatArrayPush(d->floatArray, cpBodyGetTorque(body));
    }
}

void pmSpaceBodySetIteratorFuncBatched(cpBody *body, void *data)
{
    pmBatchedData *d = (pmBatchedData *)data;

    if (d->fields & BODY_ID)
    {
        // Ignored. Not possible to set Body ID
    }
    if (d->fields & POSITION)
    {
        cpBodySetPosition(body, pmFloatArrayPopVect(d->floatArray));
    }
    if (d->fields & ANGLE)
    {
        cpBodySetAngle(body, pmFloatArrayPop(d->floatArray));
    }
    if (d->fields & VELOCITY)
    {
        cpBodySetVelocity(body, pmFloatArrayPopVect(d->floatArray));
    }
    if (d->fields & ANGULAR_VELOCITY)
    {
        cpBodySetAngularVelocity(body, pmFloatArrayPop(d->floatArray));
    }
    if (d->fields & FORCE)
    {
        cpBodySetForce(body, pmFloatArrayPopVect(d->floatArray));
    }
    if (d->fields & TORQUE)
    {
        cpBodySetTorque(body, pmFloatArrayPop(d->floatArray));
    }
}

void pmSpaceArbiterIteratorFuncBatched(cpArbiter *arbiter, void *data)
{
    pmBatchedData *d = (pmBatchedData *)data;

    if (d->fields & (BODY_A_ID | BODY_B_ID))
    {
        cpBody *a;
        cpBody *b;
        cpArbiterGetBodies(arbiter, &a, &b);

        if (d->fields & BODY_A_ID)
        {
            pmIntArrayPush(d->intArray, (uintptr_t)cpBodyGetUserData(a));
        }
        if (d->fields & BODY_B_ID)
        {
            pmIntArrayPush(d->intArray, (uintptr_t)cpBodyGetUserData(b));
        }
    }

    if (d->fields & TOTAL_IMPULSE)
    {
        pmFloatArrayPushVect(d->floatArray, cpArbiterTotalImpulse(arbiter));
    }
    if (d->fields & TOTAL_KE)
    {
        pmFloatArrayPush(d->floatArray, cpArbiterTotalKE(arbiter));
    }
    if (d->fields & IS_FIRST_CONTACT)
    {
        pmIntArrayPush(d->intArray, cpArbiterIsFirstContact(arbiter));
    }
    if (d->fields & NORMAL)
    {
        pmFloatArrayPushVect(d->floatArray, cpArbiterGetNormal(arbiter));
    }
    if (d->fields & CONTACT_COUNT)
    {
        pmIntArrayPush(d->intArray, cpArbiterGetCount(arbiter));
    }
    if (d->fields & POINT_A_1)
    {
        if (cpArbiterGetCount(arbiter) > 0)
        {
            pmFloatArrayPushVect(d->floatArray, cpArbiterGetPointA(arbiter, 0));
        }
        else
        {
            pmFloatArrayPushVect(d->floatArray, cpv(0, 0));
        }
    }
    if (d->fields & POINT_B_1)
    {
        if (cpArbiterGetCount(arbiter) > 0)
        {
            pmFloatArrayPushVect(d->floatArray, cpArbiterGetPointB(arbiter, 0));
        }
        else
        {
            pmFloatArrayPushVect(d->floatArray, cpv(0, 0));
        }
    }
    if (d->fields & DISTANCE_1)
    {
        if (cpArbiterGetCount(arbiter) > 0)
        {
            pmFloatArrayPush(d->floatArray, cpArbiterGetDepth(arbiter, 0));
        }
        else
        {
            pmFloatArrayPush(d->floatArray, 0);
        }
    }
    if (d->fields & POINT_A_2)
    {
        if (cpArbiterGetCount(arbiter) == 2)
        {
            pmFloatArrayPushVect(d->floatArray, cpArbiterGetPointA(arbiter, 1));
        }
        else
        {
            pmFloatArrayPushVect(d->floatArray, cpv(0, 0));
        }
    }
    if (d->fields & POINT_B_2)
    {
        if (cpArbiterGetCount(arbiter) == 2)
        {
            pmFloatArrayPushVect(d->floatArray, cpArbiterGetPointB(arbiter, 1));
        }
        else
        {
            pmFloatArrayPushVect(d->floatArray, cpv(0, 0));
        }
    }
    if (d->fields & DISTANCE_2)
    {
        if (cpArbiterGetCount(arbiter) == 2)
        {
            pmFloatArrayPush(d->floatArray, cpArbiterGetDepth(arbiter, 1));
        }
        else
        {
            pmFloatArrayPush(d->floatArray, 0);
        }
    }
}

//
// Functions to support pickle of arbiters the space has cached
//
typedef struct cpContact cpContact;

cpHashValue cpShapeGetHashID(cpShape *shape)
{
    return shape->hashid;
}
void cpShapeSetHashID(cpShape *shape, cpHashValue id)
{
    shape->hashid = id;
}

cpHashValue cpSpaceGetShapeIDCounter(cpSpace *space)
{
    return space->shapeIDCounter;
}
void cpSpaceSetShapeIDCounter(cpSpace *space, cpHashValue counter)
{
    space->shapeIDCounter = counter;
}

cpTimestamp cpSpaceGetTimestamp(cpSpace *space)
{
    return space->stamp;
}

void cpSpaceSetTimestamp(cpSpace *space, cpTimestamp stamp)
{
    space->stamp = stamp;
}

void cpSpaceSetCurrentTimeStep(cpSpace *space, cpFloat curr_dt)
{
    space->curr_dt = curr_dt;
}

typedef void (*cpArbiterIteratorFunc)(cpArbiter *arb, void *data);

void cpSpaceEachCachedArbiter(cpSpace *space, cpArbiterIteratorFunc func, void *data)
{
    cpHashSetEach(space->cachedArbiters, (cpHashSetIteratorFunc)func, data);
}

static inline cpCollisionHandler *
cpSpaceLookupHandler(cpSpace *space, cpCollisionType a, cpCollisionType b)
{
    cpCollisionType types[] = {a, b};
    cpCollisionHandler *handler = (cpCollisionHandler *)cpHashSetFind(space->collisionHandlers, CP_HASH_PAIR(a, b), types);
    return (handler ? handler : &cpCollisionHandlerDoNothing);
}

void cpSpaceAddCachedArbiter(cpSpace *space, cpArbiter *arb)
{
    // Need to init the contact buffer
    cpSpacePushFreshContactBuffer(space);

    int numContacts = arb->count;
    struct cpContact *contacts = arb->contacts;
    // Restore contact values back to the space's contact buffer memory
    arb->contacts = cpContactBufferGetArray(space);

    memcpy(arb->contacts, contacts, numContacts * sizeof(struct cpContact));
    cpSpacePushContacts(space, numContacts);

    // Reinsert the arbiter into the arbiter cache
    const cpShape *a = arb->a, *b = arb->b;
    const cpShape *shape_pair[] = {a, b};
    cpHashValue arbHashID = CP_HASH_PAIR((cpHashValue)a, (cpHashValue)b);
    cpHashSetInsert(space->cachedArbiters, arbHashID, shape_pair, NULL, arb);

    // Set handlers to their defaults
    cpCollisionType typeA = a->type, typeB = b->type;
    //cpCollisionHandler *handler = arb->handler = cpSpaceLookupHandler(space, typeA, typeB);
	arb->handlerAB = cpSpaceLookupHandler(space, typeA, typeB);
	arb->handlerA = cpSpaceLookupHandler(space, typeA, CP_WILDCARD_COLLISION_TYPE);

	if (typeA != typeB){
		arb->handlerBA = cpSpaceLookupHandler(space, typeB, typeA);
		arb->handlerB = cpSpaceLookupHandler(space, typeB, CP_WILDCARD_COLLISION_TYPE);
	} else{
		arb->handlerBA = &cpCollisionHandlerDoNothing;
		arb->handlerB = &cpCollisionHandlerDoNothing;
	}
	arb->swapped = (typeA != arb->handlerAB->typeA);

    // Check if the types match, but don't swap for a default handler which use the wildcard for type A.
    //cpBool swapped = arb->swapped = (typeA != handler->typeA && handler->typeA != CP_WILDCARD_COLLISION_TYPE);

    // The order of the main handler swaps the wildcard handlers too. Uffda.
    //arb->handlerA = cpSpaceLookupHandler(space, (swapped ? typeB : typeA), CP_WILDCARD_COLLISION_TYPE);
    //arb->handlerB = cpSpaceLookupHandler(space, (swapped ? typeA : typeB), CP_WILDCARD_COLLISION_TYPE);

    // Update the arbiter's state
    cpArrayPush(space->arbiters, arb);

    cpfree(contacts);
}

cpArbiter *cpArbiterNew(cpShape *a, cpShape *b)
{
    cpArbiter *arb = (cpArbiter *)cpcalloc(1, sizeof(struct cpArbiter));
    return cpArbiterInit(arb, a, b);
}

cpContact *cpContactArrAlloc(int count)
{
    return (cpContact *)cpcalloc(count, sizeof(struct cpContact));
}

cpFloat defaultSpringForce(cpDampedSpring *spring, cpFloat dist){
	return (spring->restLength - dist)*spring->stiffness;
}

cpFloat defaultSpringTorque(cpDampedRotarySpring *spring, cpFloat relativeAngle){
	return (relativeAngle - spring->restAngle)*spring->stiffness;
}


//
// Functions to forward logs (printfs) to python code instead of directly printing to stderr
//

//Python side, already formatted message
static void ext_pyLog(const char *formattedMessage); 

//Chipmunk side, follows existing function declaration
void cpMessage(const char *condition, const char *file, int line, int isError, int isHardError, const char *message, ...)
{
   	ext_pyLog((isError ? "Aborting due to Chipmunk error: " : "Chipmunk warning: "));
    
    static char formattedMessage[256];
    formattedMessage[0] = 0;

    va_list vargs;
	va_start(vargs, message); {	
        vsnprintf(formattedMessage, sizeof(formattedMessage), message, vargs);
		ext_pyLog(formattedMessage);
	} va_end(vargs);
    
    snprintf(formattedMessage, sizeof(formattedMessage), "\tFailed condition: %s", condition);
	ext_pyLog(formattedMessage);
	
    snprintf(formattedMessage, sizeof(formattedMessage), "\tSource: %s:%d", file, line);
	ext_pyLog(formattedMessage);	
}

static void DoNothing(cpArbiter *arb, cpSpace *space, cpDataPointer data){}