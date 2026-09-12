# เอกซ์แทรกเตอร์

ฟังก์ชันฝั่งเซิร์ฟเวอร์ที่เราดูในบทที่แล้วแสดงวิธีรันโค้ดบนเซิร์ฟเวอร์และผสานรวมกับส่วนติดต่อผู้ใช้ที่คุณเรนเดอร์ในเบราว์เซอร์ แต่มันไม่ได้แสดงให้คุณเห็นมากนักเกี่ยวกับวิธีใช้เซิร์ฟเวอร์ของคุณให้เต็มศักยภาพจริงๆ

## เซิร์ฟเวอร์เฟรมเวิร์ก

เราเรียก Leptos ว่าเฟรมเวิร์ก “ฟูลสแตก” แต่คำว่า “ฟูลสแตก” มักเป็นชื่อเรียกที่ไม่ตรงเสียทีเดียว (ไม่เช่นนั้นมันคงไม่หมายถึงทุกอย่างตั้งแต่เบราว์เซอร์ไปจนถึงบริษัทไฟฟ้าของคุณ) สำหรับเรา “ฟูลสแตก” หมายความว่าแอป Leptos ของคุณสามารถรันในเบราว์เซอร์ และรันบนเซิร์ฟเวอร์ และผสานรวมทั้งสองเข้าด้วยกัน โดยดึงจุดเด่นที่ไม่เหมือนใครของแต่ละฝ่ายมารวมกัน; อย่างที่เราเห็นในหนังสือเล่มนี้มาแล้ว การคลิกปุ่มบนเบราว์เซอร์สามารถขับเคลื่อนการอ่านฐานข้อมูลบนเซิร์ฟเวอร์ โดยทั้งคู่เขียนในโมดูล Rust เดียวกัน แต่ Leptos เองไม่ได้จัดหาเซิร์ฟเวอร์ (หรือฐานข้อมูล หรือระบบปฏิบัติการ หรือเฟิร์มแวร์ หรือสายไฟ...)

แต่ Leptos มีการผสานรวมสำหรับเว็บเซิร์ฟเวอร์เฟรมเวิร์ก Rust ยอดนิยมสองตัว คือ Actix Web ([`leptos_actix`](https://docs.rs/leptos_actix/latest/leptos_actix/)) และ Axum ([`leptos_axum`](https://docs.rs/leptos_axum/latest/leptos_axum/)) เราได้สร้างการผสานรวมกับเราเตอร์ของแต่ละเซิร์ฟเวอร์ เพื่อให้คุณเพียงเสียบแอป Leptos ของคุณเข้ากับเซิร์ฟเวอร์ที่มีอยู่ด้วย `.leptos_routes()` และจัดการการเรียกฟังก์ชันฝั่งเซิร์ฟเวอร์ได้อย่างง่ายดาย

> ถ้าคุณยังไม่เคยเห็นเทมเพลต [Actix](https://github.com/leptos-rs/start-actix) และ [Axum](https://github.com/leptos-rs/start-axum) ของเรา ตอนนี้เป็นเวลาที่ดีที่จะลองดู

## การใช้เอกซ์แทรกเตอร์

ทั้งตัวจัดการของ Actix และ Axum ต่างสร้างอยู่บนแนวคิดอันทรงพลังเดียวกันคือ**เอกซ์แทรกเตอร์** เอกซ์แทรกเตอร์ “สกัด” ข้อมูลที่มีชนิดจากคำขอ HTTP ทำให้คุณเข้าถึงข้อมูลเฉพาะเซิร์ฟเวอร์ได้อย่างง่ายดาย

Leptos มีฟังก์ชันช่วย `extract` เพื่อให้คุณใช้เอกซ์แทรกเตอร์เหล่านี้ได้โดยตรงในฟังก์ชันฝั่งเซิร์ฟเวอร์ของคุณ ด้วยไวยากรณ์ที่สะดวกซึ่งคล้ายกับตัวจัดการของแต่ละเฟรมเวิร์กมาก

### เอกซ์แทรกเตอร์ของ Actix

[ฟังก์ชัน `extract` ใน `leptos_actix`](https://docs.rs/leptos_actix/latest/leptos_actix/fn.extract.html) รับฟังก์ชันตัวจัดการเป็นอาร์กิวเมนต์ ตัวจัดการมีกฎคล้ายกับตัวจัดการของ Actix: มันเป็นฟังก์ชัน async ที่รับอาร์กิวเมนต์ที่จะถูกสกัดจากคำขอ และคืนค่าบางอย่าง ฟังก์ชันตัวจัดการรับข้อมูลที่สกัดมาเป็นอาร์กิวเมนต์ของมัน และสามารถทำงาน `async` เพิ่มเติมกับข้อมูลเหล่านั้นภายในเนื้อความของบล็อก `async move` ได้ มันคืนค่าอะไรก็ตามที่คุณคืนกลับออกมาสู่ฟังก์ชันฝั่งเซิร์ฟเวอร์

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

ไวยากรณ์ของฟังก์ชัน [`leptos_axum::extract`](https://docs.rs/leptos_axum/latest/leptos_axum/fn.extract.html) คล้ายกันมาก

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

ตัวอย่างเหล่านี้ค่อนข้างเรียบง่าย โดยเข้าถึงข้อมูลพื้นฐานจากเซิร์ฟเวอร์ แต่คุณสามารถใช้เอกซ์แทรกเตอร์เพื่อเข้าถึงสิ่งอย่าง headers, คุกกี้, พูลการเชื่อมต่อฐานข้อมูล และอื่นๆ ได้ โดยใช้แพตเทิร์น `extract()` เดียวกันนี้

ฟังก์ชัน `extract` ของ Axum รองรับเฉพาะเอกซ์แทรกเตอร์ที่ state เป็น `()` เท่านั้น หากคุณต้องการเอกซ์แทรกเตอร์ที่ใช้ `State` คุณควรใช้ [`extract_with_state`](https://docs.rs/leptos_axum/latest/leptos_axum/fn.extract_with_state.html) ซึ่งต้องให้คุณระบุ state คุณทำได้โดยขยาย state `LeptosOptions` ที่มีอยู่โดยใช้แพตเทิร์น `FromRef` ของ Axum ซึ่งให้ state เป็นคอนเท็กซ์ระหว่างการเรนเดอร์และฟังก์ชันฝั่งเซิร์ฟเวอร์ด้วยตัวจัดการแบบกำหนดเอง

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

[คลิกที่นี่เพื่อดูตัวอย่างการให้คอนเท็กซ์ในตัวจัดการแบบกำหนดเอง](https://github.com/leptos-rs/leptos/blob/19ea6fae6aec2a493d79cc86612622d219e6eebb/examples/session_auth_axum/src/main.rs#L24-L44)

#### State ของ Axum

แพตเทิร์นทั่วไปของ Axum สำหรับการฉีดดีเพนเดนซีคือการให้ `State` ซึ่งสามารถสกัดได้ในตัวจัดการเส้นทางของคุณ Leptos มีวิธีฉีดดีเพนเดนซีเป็นของตัวเองผ่านคอนเท็กซ์ คอนเท็กซ์มักใช้แทน `State` เพื่อให้ข้อมูลเซิร์ฟเวอร์ที่ใช้ร่วมกันได้ (ตัวอย่างเช่น พูลการเชื่อมต่อฐานข้อมูล)

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

คอนเท็กซ์นี้สามารถเข้าถึงได้ด้วย `use_context::<T>()` ง่ายๆ ภายในฟังก์ชันฝั่งเซิร์ฟเวอร์ของคุณ

ถ้าคุณ_จำเป็น_ต้องใช้ `State` ในฟังก์ชันฝั่งเซิร์ฟเวอร์ ตัวอย่างเช่น ถ้าคุณมีเอกซ์แทรกเตอร์ของ Axum ที่มีอยู่ซึ่งต้องใช้ `State` ก็ทำได้เช่นกันโดยใช้แพตเทิร์น [`FromRef`](https://docs.rs/axum/latest/axum/extract/derive.FromRef.html) ของ Axum และ [`extract_with_state`](https://docs.rs/leptos_axum/latest/leptos_axum/fn.extract_with_state.html) โดยพื้นฐานแล้วคุณจะต้องให้ state ทั้งผ่านคอนเท็กซ์และผ่าน state ของเราเตอร์ Axum:

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

ในบางกรณี คุณอาจต้องการใช้ชนิดเจเนอริกสำหรับ state ของคุณ มาใช้ตัวอย่างต่อไปนี้:

```rust
pub struct AppState<TS: ThingService> {
    pub thing_service: Arc<TS>,
} 
```

ใน Axum โดยทั่วไปคุณจะใช้พารามิเตอร์เจเนอริกกับตัวจัดการของคุณแบบนี้:

```rust
pub async fn do_thing<TS: ThingService>(
    State(state): State<AppState<TS>>,
) -> Result<(), ThingError> {
    state.thing_service.do_thing()
}
```

น่าเสียดายที่พารามิเตอร์เจเนอริกยังไม่ได้รับการรองรับในฟังก์ชันฝั่งเซิร์ฟเวอร์ของ Leptos ในปัจจุบัน อย่างไรก็ตาม คุณสามารถเลี่ยงข้อจำกัดนี้ได้โดยใช้ชนิดที่เป็นรูปธรรมในฟังก์ชันฝั่งเซิร์ฟเวอร์ของคุณเพื่อเรียกฟังก์ชันเจเนอริกภายใน นี่คือวิธีที่คุณทำได้:

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

เนื่องจาก Actix และ (โดยเฉพาะ) Axum สร้างขึ้นบนแนวคิดของการส่งคำขอและรับการตอบกลับ HTTP แบบไปกลับครั้งเดียว คุณมักจะรันเอกซ์แทรกเตอร์ใกล้ “ด้านบน” ของแอปพลิเคชันของคุณ (กล่าวคือ ก่อนที่คุณจะเริ่มเรนเดอร์) และใช้ข้อมูลที่สกัดมาเพื่อกำหนดว่าควรเรนเดอร์อย่างไร ก่อนที่คุณจะเรนเดอร์ `<button>` คุณโหลดข้อมูลทั้งหมดที่แอปของคุณอาจต้องใช้ และตัวจัดการเส้นทางใดๆ ก็ต้องรู้ข้อมูลทั้งหมดที่เส้นทางนั้นจะต้องสกัด

แต่ Leptos ผสานรวมทั้งไคลเอนต์และเซิร์ฟเวอร์ และการสามารถรีเฟรชชิ้นส่วนเล็กๆ ของ UI ด้วยข้อมูลใหม่จากเซิร์ฟเวอร์โดยไม่บังคับให้โหลดข้อมูลทั้งหมดใหม่นั้นสำคัญมาก ดังนั้น Leptos จึงชอบดันการโหลดข้อมูล “ลงล่าง” ในแอปพลิเคชันของคุณ ให้ไกลไปทางใบของส่วนติดต่อผู้ใช้มากที่สุดเท่าที่จะเป็นไปได้ เมื่อคุณคลิก `<button>` มันสามารถรีเฟรชเฉพาะข้อมูลที่มันต้องการได้ นี่คือสิ่งที่ฟังก์ชันฝั่งเซิร์ฟเวอร์มีไว้เพื่อ: พวกมันให้การเข้าถึงข้อมูลที่จะโหลดและโหลดใหม่ในระดับละเอียด

ฟังก์ชัน `extract()` ช่วยให้คุณผสานทั้งสองโมเดลโดยใช้เอกซ์แทรกเตอร์ในฟังก์ชันฝั่งเซิร์ฟเวอร์ของคุณ คุณได้รับพลังเต็มรูปแบบของเอกซ์แทรกเตอร์เส้นทาง ขณะเดียวกันก็กระจายความรู้เกี่ยวกับสิ่งที่ต้องสกัดลงไปยังคอมโพเนนต์แต่ละตัวของคุณ สิ่งนี้ทำให้การรีแฟกเตอร์และจัดระเบียบเส้นทางง่ายขึ้น: คุณไม่จำเป็นต้องระบุข้อมูลทั้งหมดที่เส้นทางต้องการไว้ล่วงหน้า
