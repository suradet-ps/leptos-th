# เอกซ์แทรกเตอร์

ฟังก์ชันฝั่งเซิร์ฟเวอร์ที่เราได้เรียนรู้ไปในบทก่อนหน้านี้ได้แสดงให้เห็นถึงวิธีการสั่งรันโค้ดบนเซิร์ฟเวอร์ และการผสานรวมเข้ากับหน้าตาอินเทอร์เฟซที่คุณกำลังเรนเดอร์บนเบราว์เซอร์ แต่ตัวอย่างเหล่านั้นยังไม่ได้แสดงให้เห็นถึงวิธีดึงศักยภาพสูงสุดของเซิร์ฟเวอร์ออกมาใช้งานอย่างเต็มที่มากนัก

## เซิร์ฟเวอร์เฟรมเวิร์ก

เรามักเรียก Leptos ว่าเป็นเฟรมเวิร์ก “ฟูลสแตก” (full-stack) แต่คำว่า “ฟูลสแตก” นั้นมักเป็นการเรียกแบบกว้างเกินจริงเสมอ (เพราะอย่างไรเสีย มันก็คงไม่ได้ครอบคลุมทุกสิ่งทุกอย่างตั้งแต่หน้าต่างเบราว์เซอร์ไปจนถึงโรงงานผลิตไฟฟ้าของคุณอย่างแน่นอน!) สำหรับเรา คำว่า “ฟูลสแตก” มีความหมายว่า แอปพลิเคชัน Leptos ของคุณสามารถทำงานได้ทั้งบนเบราว์เซอร์และบนเซิร์ฟเวอร์ อีกทั้งยังสามารถผสานการทำงานของทั้งสองฝั่งเข้าด้วยกัน เพื่อดึงเอาจุดเด่นเฉพาะตัวของแต่ละฝั่งมาร่วมมือกันได้อย่างลงตัว ดังที่เราได้เห็นกันไปแล้วในหนังสือเล่มนี้ว่า การคลิกปุ่มเพียงครั้งเดียวบนเบราว์เซอร์สามารถส่งผลให้เกิดการอ่านข้อมูลจากฐานข้อมูลบนเซิร์ฟเวอร์ได้ โดยที่โค้ดทั้งสองส่วนถูกเขียนอยู่ในโมดูลภาษา Rust เดียวกัน ทว่าตัว Leptos เองไม่ได้มีเว็บเซิร์ฟเวอร์ในตัว (เช่นเดียวกับที่ไม่ได้มีฐานข้อมูล, ระบบปฏิบัติการ, เฟิร์มแวร์ หรือสายเคเบิลไฟฟ้าในตัว...)

สิ่งที่ Leptos มอบให้แทน คือการผสานการทำงานร่วมกับเว็บเซิร์ฟเวอร์เฟรมเวิร์กยอดนิยมสองตัวของวงการ Rust นั่นคือ Actix Web ([`leptos_actix`](https://docs.rs/leptos_actix/latest/leptos_actix/)) และ Axum ([`leptos_axum`](https://docs.rs/leptos_axum/latest/leptos_axum/)) โดยเราได้สร้างตัวเชื่อมต่อเข้ากับเราเตอร์ของแต่ละเซิร์ฟเวอร์ เพื่อให้คุณสามารถนำแอป Leptos ไปเสียบเข้ากับเซิร์ฟเวอร์ที่มีอยู่เดิมได้อย่างง่ายดายผ่าน `.leptos_routes()` และจัดการกับการเรียกใช้งานฟังก์ชันฝั่งเซิร์ฟเวอร์ได้อย่างสะดวกสบาย

> หากคุณยังไม่เคยเห็นโปรเจกต์เทมเพลตเริ่มต้นของเราสำหรับ [Actix](https://github.com/leptos-rs/start-actix) และ [Axum](https://github.com/leptos-rs/start-axum) ตอนนี้ถือเป็นโอกาสอันดีที่จะเข้าไปศึกษาเพิ่มเติม

## การใช้เอกซ์แทรกเตอร์

ทั้งตัวจัดการคำขอ (handler) ของ Actix และ Axum ต่างสร้างขึ้นบนแนวคิดอันทรงพลังเดียวกัน นั่นคือ **เอกซ์แทรกเตอร์ (extractors)** โดยเอกซ์แทรกเตอร์จะทำหน้าที่ “สกัด” ข้อมูลที่มีชนิดข้อมูลแน่นอน (typed data) ออกมาจากคำขอ HTTP ช่วยให้คุณสามารถเข้าถึงข้อมูลเฉพาะทางของฝั่งเซิร์ฟเวอร์ได้อย่างง่ายดาย

Leptos ได้เตรียมฟังก์ชันตัวช่วย `extract` ไว้ให้ เพื่อให้คุณสามารถเรียกใช้งานเอกซ์แทรกเตอร์เหล่านี้ได้โดยตรงจากภายในฟังก์ชันฝั่งเซิร์ฟเวอร์ ด้วยไวยากรณ์ที่สะดวกสบายและคล้ายคลึงกับตัวจัดการคำขอของแต่ละเฟรมเวิร์กเป็นอย่างยิ่ง

### เอกซ์แทรกเตอร์ของ Actix

[ฟังก์ชัน `extract` ใน `leptos_actix`](https://docs.rs/leptos_actix/latest/leptos_actix/fn.extract.html) จะรับฟังก์ชันตัวจัดการเป็นอาร์กิวเมนต์ โดยตัวจัดการนี้จะมีกฎคล้ายคลึงกับตัวจัดการทั่วไปของ Actix: นั่นคือเป็นฟังก์ชัน async ที่รับอาร์กิวเมนต์ซึ่งจะถูกสกัดออกมาจากคำขอ และส่งคืนค่าบางอย่างกลับไป ฟังก์ชันตัวจัดการจะได้รับข้อมูลที่สกัดแล้วเข้ามาทางอาร์กิวเมนต์ และสามารถนำข้อมูลเหล่านั้นไปประมวลผลแบบ `async` เพิ่มเติมได้ภายในเนื้อหาของบล็อก `async move` ก่อนจะส่งค่าใดก็ตามที่คุณคืนกลับออกมา ส่งต่อไปยังฟังก์ชันฝั่งเซิร์ฟเวอร์อีกทอดหนึ่ง

```rust
use serde::Deserialize;

#[derive(Deserialize, Debug)]
struct MyQuery {
    foo: String,
}

#[server]
pub async fn actix_extract() -> Result<String, ServerFnError> {
    use actix_web::dev::ConnectionInfo;
    use actix_web::web::Query;
    use leptos_actix::extract;

    let (Query(search), connection): (Query<MyQuery>, ConnectionInfo) = extract().await?;
    Ok(format!("search = {search:?}\nconnection = {connection:?}",))
}
```

### เอกซ์แทรกเตอร์ของ Axum

ไวยากรณ์ของฟังก์ชัน [`leptos_axum::extract`](https://docs.rs/leptos_axum/latest/leptos_axum/fn.extract.html) ก็มีความคล้ายคลึงกันอย่างมาก:

```rust
use serde::Deserialize;

#[derive(Deserialize, Debug)]
struct MyQuery {
    foo: String,
}

#[server]
pub async fn axum_extract() -> Result<String, ServerFnError> {
    use axum::{extract::Query, http::Method};
    use leptos_axum::extract;

    let (method, query): (Method, Query<MyQuery>) = extract().await?;

    Ok(format!("{method:?} and {query:?}"))
}
```

ตัวอย่างข้างต้นเป็นเพียงตัวอย่างแบบง่ายในการเข้าถึงข้อมูลพื้นฐานจากเซิร์ฟเวอร์ แต่ในความเป็นจริง คุณสามารถใช้เอกซ์แทรกเตอร์เพื่อเข้าถึงข้อมูลส่วนหัว (headers), คุกกี้ (cookies), พูลการเชื่อมต่อฐานข้อมูล (database connection pools) และอื่น ๆ อีกมากมายได้ โดยใช้รูปแบบ `extract()` เดียวกันนี้

ฟังก์ชัน `extract` ของ Axum จะรองรับเฉพาะเอกซ์แทรกเตอร์ที่ state เป็นชนิด `()` เท่านั้น หากคุณต้องการใช้งานเอกซ์แทรกเตอร์ที่ต้องพึ่งพา `State` คุณจะต้องเปลี่ยนไปใช้ [`extract_with_state`](https://docs.rs/leptos_axum/latest/leptos_axum/fn.extract_with_state.html) แทน ซึ่งจะบังคับให้คุณต้องส่ง state เข้าไปด้วย คุณสามารถทำได้โดยการขยาย state `LeptosOptions` ที่มีอยู่เดิมผ่านรูปแบบ `FromRef` ของ Axum ซึ่งจะส่งต่อ state นั้นไปให้เป็นคอนเทกซ์ระหว่างขั้นตอนการเรนเดอร์ และส่งต่อไปยังฟังก์ชันฝั่งเซิร์ฟเวอร์ที่มีตัวจัดการแบบกำหนดเอง

```rust
use axum::extract::FromRef;

/// Derive FromRef to allow multiple items in state, using Axum’s
/// SubStates pattern.
#[derive(FromRef, Debug, Clone)]
pub struct AppState{
    pub leptos_options: LeptosOptions,
    pub pool: SqlitePool
}
```

[คลิกที่นี่เพื่อดูตัวอย่างการส่งต่อคอนเทกซ์ในตัวจัดการแบบกำหนดเอง](https://github.com/leptos-rs/leptos/blob/19ea6fae6aec2a493d79cc86612622d219e6eebb/examples/session_auth_axum/src/main.rs#L24-L44)

#### State ของ Axum

รูปแบบมาตรฐานของ Axum ในการทำ dependency injection คือการส่งผ่าน `State` ซึ่งสามารถสกัดออกมาใช้งานได้ภายในตัวจัดการเส้นทางของคุณ ส่วน Leptos นั้นมีกลไก dependency injection เป็นของตัวเองผ่านระบบคอนเทกซ์ (context) ซึ่งโดยส่วนใหญ่แล้ว เรามักใช้คอนเทกซ์แทนที่ `State` เพื่อส่งผ่านข้อมูลที่ใช้ร่วมกันบนเซิร์ฟเวอร์ (เช่น พูลการเชื่อมต่อฐานข้อมูล)

```rust
let connection_pool = /* some shared state here */;

let app = Router::new()
    .leptos_routes_with_context(
        &leptos_options,
        routes,
        move || provide_context(connection_pool.clone()),
        {
            let leptos_options = leptos_options.clone();
            move || shell(leptos_options.clone())
        },
    )
    // etc.
```

จากนั้น คุณสามารถเข้าถึงคอนเทกซ์นี้ได้ง่าย ๆ ผ่านคำสั่ง `use_context::<T>()` จากภายในฟังก์ชันฝั่งเซิร์ฟเวอร์ของคุณ

แต่หากคุณ *จำเป็น* ต้องใช้ `State` ภายในฟังก์ชันฝั่งเซิร์ฟเวอร์จริง ๆ—เช่น กรณีที่คุณมีเอกซ์แทรกเตอร์เดิมของ Axum ที่บังคับว่าต้องใช้ `State`—ก็สามารถทำได้เช่นกันโดยใช้รูปแบบ [`FromRef`](https://docs.rs/axum/latest/axum/extract/derive.FromRef.html) ของ Axum ร่วมกับ [`extract_with_state`](https://docs.rs/leptos_axum/latest/leptos_axum/fn.extract_with_state.html) โดยหลักการแล้ว คุณจะต้องจัดเตรียม state ส่งผ่านไปทั้งทางคอนเทกซ์และทาง state ของเราเตอร์ Axum:

```rust
#[derive(FromRef, Debug, Clone)]
pub struct MyData {
    pub value: usize,
    pub leptos_options: LeptosOptions,
}

let app_state = MyData {
    value: 42,
    leptos_options,
};

// build our application with a route
let app = Router::new()
    .leptos_routes_with_context(
        &app_state,
        routes,
        {
            let app_state = app_state.clone();
            move || provide_context(app_state.clone())
        },
        App,
    )
    .fallback(file_and_error_handler)
    .with_state(app_state);

// ...
#[server]
pub async fn uses_state() -> Result<(), ServerFnError> {
    let state = expect_context::<MyData>();
    let SomeStateExtractor(data) = extract_with_state(&state).await?;
    // todo
}
```

#### State แบบเจเนอริก

ในบางกรณี คุณอาจต้องการใช้ชนิดข้อมูลแบบเจเนอริกสำหรับ state ของคุณ ลองพิจารณาตัวอย่างต่อไปนี้:

```rust
pub struct AppState<TS: ThingService> {
    pub thing_service: Arc<TS>,
} 
```

ใน Axum โดยทั่วไปคุณมักจะกำหนดพารามิเตอร์เจเนอริกไว้ที่ตัวจัดการของคุณในลักษณะนี้:

```rust
pub async fn do_thing<TS: ThingService>(
    State(state): State<AppState<TS>>,
) -> Result<(), ThingError> {
    state.thing_service.do_thing()
}
```

แต่น่าเสียดายที่ในปัจจุบัน ฟังก์ชันฝั่งเซิร์ฟเวอร์ของ Leptos ยังไม่รองรับพารามิเตอร์เจเนอริกโดยตรง อย่างไรก็ตาม คุณสามารถเลี่ยงข้อจำกัดนี้ได้โดยการระบุชนิดข้อมูลที่เป็นรูปธรรม (concrete type) ภายในฟังก์ชันฝั่งเซิร์ฟเวอร์ เพื่อส่งต่อไปเรียกใช้ฟังก์ชันเจเนอริกตัวในอีกทีหนึ่ง ดังแนวทางต่อไปนี้:

```rust
pub async do_thing_inner<TS: ThingService>() -> Result<(), ServerFnError> {
    let state = expect_context::<AppState<TS>>(); // Works!
    state.thing_service.do_thing()
}

#[server]
pub async do_thing() -> Result<(), ServerFnError> {
    use crate::thing::service::Service as ConcreteThingService;
    use crate::thing::some_dep::SomeDep;

    do_thing_inner::<ConcreteThingService<SomeDep>>().await
}
```

## หมายเหตุเกี่ยวกับแพตเทิร์นการโหลดข้อมูล

เนื่องจาก Actix และ (โดยเฉพาะอย่างยิ่ง) Axum ถูกสร้างขึ้นบนแนวคิดของคำขอและการตอบกลับ HTTP แบบไป-กลับหนึ่งรอบ (single round-trip request/response) คุณจึงมักจะสั่งรันเอกซ์แทรกเตอร์อยู่ที่บริเวณ “ส่วนบนสุด” ของแอปพลิเคชัน (นั่นคือ ก่อนที่จะเริ่มต้นการเรนเดอร์) แล้วนำข้อมูลที่สกัดได้นั้นมาตัดสินใจว่าจะเรนเดอร์หน้าตาออกมาอย่างไร กล่าวคือ ก่อนที่คุณจะเรนเดอร์ปุ่ม `<button>` คุณจะต้องโหลดข้อมูลทั้งหมดที่แอปอาจต้องใช้มาเตรียมไว้ล่วงหน้า และตัวจัดการเส้นทางใด ๆ จะต้องทราบข้อมูลทั้งหมดที่จำเป็นต้องถูกสกัดสำหรับเส้นทางนั้นตั้งแต่แรก

แต่ Leptos นั้นผสานการทำงานของทั้งฝั่งไคลเอนต์และฝั่งเซิร์ฟเวอร์เข้าด้วยกัน และสิ่งสำคัญคือการเปิดโอกาสให้คุณสามารถรีเฟรชเฉพาะชิ้นส่วนเล็ก ๆ ของ UI ด้วยข้อมูลชุดใหม่จากเซิร์ฟเวอร์ได้ โดยไม่ต้องบีบให้ต้องโหลดข้อมูลทั้งหมดของทั้งหน้าใหม่อีกครั้ง ด้วยเหตุนี้ Leptos จึงนิยมผลักดันการโหลดข้อมูลให้ลงไปอยู่ “ด้านล่าง” ของแอปพลิเคชันให้มากที่สุด เท่าที่จะเข้าใกล้โหนดปลายทาง (leaves) ของหน้าตาอินเทอร์เฟซได้ เมื่อผู้ใช้คลิกปุ่ม `<button>` ระบบจึงสามารถรีเฟรชเฉพาะข้อมูลที่ปุ่มนั้นต้องการจริง ๆ ได้ทันที และนี่คือจุดประสงค์ที่แท้จริงของฟังก์ชันฝั่งเซิร์ฟเวอร์: เพื่อมอบการเข้าถึงข้อมูลในระดับละเอียด (granular) สำหรับทั้งการโหลดข้อมูลครั้งแรกและการโหลดซ้ำ

ฟังก์ชัน `extract()` ช่วยให้คุณสามารถผสานทั้งสองโมเดลเข้าด้วยกันได้ โดยการนำเอกซ์แทรกเตอร์มาใช้งานภายในฟังก์ชันฝั่งเซิร์ฟเวอร์ของคุณ คุณจึงได้รับขุมพลังเต็มเปี่ยมของเอกซ์แทรกเตอร์ระดับเส้นทาง ในขณะเดียวกันก็สามารถกระจายความรับผิดชอบในการสกัดข้อมูลลงไปไว้ที่คอมโพเนนต์แต่ละชิ้นได้อย่างอิสระ ทำให้การปรับโครงสร้างโค้ด (refactor) และการจัดระเบียบเส้นทางทำได้ง่ายดายยิ่งขึ้น โดยไม่จำเป็นต้องมาระบุข้อมูลทั้งหมดที่เส้นทางต้องการไว้ล่วงหน้าตั้งแต่แรกเริ่ม
