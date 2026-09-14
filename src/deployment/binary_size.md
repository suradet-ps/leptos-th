# การปรับขนาดไบนารี WASM ให้เหมาะสม

ไบนารี WebAssembly มักมีขนาดใหญ่กว่า JavaScript bundle ของแอปพลิเคชันที่ทำงานเทียบเท่ากันอย่างเห็นได้ชัด ทว่าด้วยโครงสร้างฟอร์แมตของ WASM ที่ถูกออกแบบมาสำหรับการคอมไพล์แบบสตรีม (streaming compilation) ไฟล์ WASM จึงคอมไพล์ได้เร็วกว่าไฟล์ JavaScript ต่อกิโลไบต์อย่างมาก (หากต้องการศึกษาเชิงลึก สามารถ[อ่านบทความยอดเยี่ยมจากทีม Mozilla](https://hacks.mozilla.org/2018/01/making-webassembly-even-faster-firefoxs-new-streaming-and-tiering-compiler/) เกี่ยวกับการคอมไพล์สตรีมมิงของ WASM ได้) อย่างไรก็ดี การส่งไบนารี WASM ให้มีขนาดเล็กที่สุดเท่าที่จะทำได้ไปยังผู้ใช้ยังคงเป็นสิ่งสำคัญยิ่ง เพราะช่วยลดการรับส่งข้อมูลผ่านเครือข่าย และทำให้แอปของคุณเริ่มมีปฏิสัมพันธ์กับผู้ใช้ได้เร็วที่สุด

แล้วในทางปฏิบัติ เรามีแนวทางและขั้นตอนอย่างไรบ้าง?

## สิ่งที่ควรทำ

1. ตรวจสอบให้แน่ใจว่าคุณกำลังวัดขนาดจากบิลด์ release (บิลด์ debug จะมีขนาดใหญ่กว่ามาก)
2. เพิ่มโปรไฟล์ release สำหรับ WASM ที่ปรับแต่งเพื่อเน้นลดขนาด มากกว่าเน้นความเร็ว

ตัวอย่างเช่น สำหรับโปรเจกต์ `cargo-leptos` คุณสามารถเพิ่มสิ่งนี้ลงใน `Cargo.toml` ของคุณได้:

```toml
[profile.wasm-release]
inherits = "release"
opt-level = 'z'
lto = true
codegen-units = 1

# ....

[package.metadata.leptos]
# ....
lib-profile-release = "wasm-release"
```

การตั้งค่านี้จะปรับแต่ง (optimize) ไบนารี WASM ในบิลด์ release ให้มีขนาดเล็กที่สุด ในขณะที่บิลด์ฝั่งเซิร์ฟเวอร์ยังคงถูกปรับแต่งเพื่อความเร็วในการประมวลผลสูงสุด (สำหรับแอปที่เป็น client-side rendering ล้วนโดยไม่มีฝั่งเซิร์ฟเวอร์ คุณสามารถนำบล็อก `[profile.wasm-release]` ไปใช้เป็น `[profile.release]` ของคุณได้เลย)

3. เสิร์ฟไฟล์ WASM แบบบีบอัด (compressed) บนโหมด production เสมอ WASM มักบีบอัดได้มีประสิทธิภาพสูงมาก โดยทั่วไปสามารถลดขนาดลงได้มากกว่า 50% จากขนาดปกติ และการเปิดใช้การบีบอัดสำหรับไฟล์สถิต (static files) บน Actix หรือ Axum นั้นทำได้ง่ายมาก

4. หากคุณใช้ nightly Rust คุณสามารถคอมไพล์สแตนดาร์ดไลบรารี (standard library) ขึ้นมาใหม่ด้วยโปรไฟล์เดียวกันนี้ แทนที่จะใช้ไลบรารีสำเร็จรูปที่มาพร้อมกับทาร์เก็ต `wasm32-unknown-unknown`

สำหรับการตั้งค่านี้ ให้สร้างไฟล์ `.cargo/config.toml` ในโปรเจกต์ของคุณ:

```toml
[unstable]
build-std = ["std", "panic_abort", "core", "alloc"]
build-std-features = ["panic_immediate_abort"]
```

โปรดทราบว่าหากคุณใช้งานร่วมกับ SSR โปรไฟล์ Cargo เดียวกันนี้จะถูกนำไปใช้กับฝั่งเซิร์ฟเวอร์ด้วย คุณจึงต้องระบุทาร์เก็ตที่ต้องการบิลด์ให้ชัดเจน:
```toml
[build]
target = "x86_64-unknown-linux-gnu" # or whatever
```

นอกจากนี้ ในบางกรณี แฟล็ก cfg `has_std` อาจไม่ได้ถูกตั้งค่าไว้ ซึ่งอาจส่งผลให้เกิดข้อผิดพลาดในการบิลด์กับดีเพนเดนซีบางตัวที่คอยตรวจเช็ก `has_std` คุณสามารถแก้ไขได้โดยเพิ่ม:
```toml
[build]
rustflags = ["--cfg=has_std"]
```

และคุณจำเป็นต้องเพิ่ม `panic = "abort"` ลงใน `[profile.release]` ของ `Cargo.toml` ด้วย แต่โปรดระลึกว่าวิธีนี้จะทำให้การตั้งค่า `build-std` และลักษณะ panic ถูกนำไปใช้กับไบนารีฝั่งเซิร์ฟเวอร์ด้วยเช่นกัน ซึ่งอาจไม่ใช่พฤติกรรมที่คุณต้องการ จึงควรทดสอบและพิจารณาเพิ่มเติมก่อนใช้งานจริง

5. อีกหนึ่งปัจจัยสำคัญที่ทำให้ขนาดไบนารี WASM บวมขึ้นคือโค้ด serialization / deserialization ของ `serde` โดยค่าเริ่มต้น Leptos จะใช้ `serde` ในการแปลงข้อมูลไปมาสำหรับทรัพยากรที่สร้างด้วย `Resource::new()` ทั้งนี้ เครต `leptos_server` มีฟีเจอร์เสริมสำหรับเปิดใช้งานการเข้ารหัสทางเลือกอื่น ๆ โดยจะเพิ่มเมธอดตระกูล `new_` เข้ามา ตัวอย่างเช่น การเปิดฟีเจอร์ `miniserde` บนเครต `leptos_server` จะเพิ่มเมธอด `Resource::new_miniserde()` เข้ามา และฟีเจอร์ `serde-lite` จะเพิ่มเมธอด `new_serde_lite` โดยทั้ง `miniserde` และ `serde-lite` นั้นจะอิมพลีเมนต์ความสามารถของ `serde` เพียงบางส่วน แต่จะเน้นลดขนาดไบนารีให้เล็กที่สุดมากกว่าเน้นความเร็ว

## สิ่งที่ควรหลีกเลี่ยง

มีเครตบางตัวที่มักจะทำให้ขนาดไบนารีใหญ่ขึ้นอย่างมาก ตัวอย่างเช่น เครต `regex` พร้อมฟีเจอร์เริ่มต้นจะเพิ่มขนาดไบนารี WASM เข้ามาอีกประมาณ 500kb (สาเหตุหลักมาจากการต้องรวมข้อมูลตาราง Unicode เข้ามาด้วย!) ในสภาพแวดล้อมที่ต้องควบคุมขนาดไบนารีอย่างเข้มงวด คุณอาจพิจารณาหลีกเลี่ยงการใช้ regex โดยไม่จำเป็น หรือหันไปเรียกใช้ browser API เพื่อใช้ regex engine ของเบราว์เซอร์แทน (ซึ่งนี่คือวิธีที่ `leptos_router` ใช้อยู่ในการประมวลผล regular expression บางจุด)

ในภาพรวม ความพยายามของ Rust ในการรีดประสิทธิภาพการทำงานขณะรันไทม์ (runtime performance) สูงสุดนั้น บางครั้งอาจสวนทางกับการลดขนาดไบนารี ตัวอย่างเช่น Rust ใช้กระบวนการ monomorphization กับฟังก์ชันเจเนอริก (generics) ซึ่งหมายความว่าคอมไพเลอร์จะสร้างสำเนาของฟังก์ชันแยกออกมาสำหรับแต่ละชนิดข้อมูลเจเนอริกที่ถูกเรียกใช้งาน วิธีนี้ทำงานเร็วกว่า dynamic dispatch อย่างมาก แต่ก็ทำให้ขนาดไบนารีใหญ่ขึ้นตามไปด้วย Leptos พยายามรักษาสมดุลระหว่างประสิทธิภาพรันไทม์กับขนาดไบนารีอย่างระมัดระวัง แต่คุณอาจพบว่าโค้ดที่ใช้ generics เป็นจำนวนมากจะส่งผลให้ไบนารีใหญ่ขึ้น ตัวอย่างเช่น หากคุณมีคอมโพเนนต์เจเนอริกที่มีโค้ดภายในยาวมาก และถูกเรียกใช้งานด้วยชนิดข้อมูลที่แตกต่างกัน 4 ชนิด คอมไพเลอร์ก็อาจสร้างโค้ดชุดเดียวกันนั้นออกมาถึง 4 สำเนา การรีแฟกเตอร์ให้หันมาใช้ inner function หรือ helper function ที่ระบุชนิดข้อมูลชัดเจน (concrete type) มักจะช่วยรักษาทั้งประสิทธิภาพ ความสะดวกในการเขียน และลดขนาดไบนารีลงได้พร้อม ๆ กัน

## การแยกโค้ด (Code Splitting)

`cargo-leptos` ร่วมกับเฟรมเวิร์กและเราเตอร์ของ Leptos รองรับการแยกไบนารี WASM ออกเป็นส่วน ๆ (WASM binary splitting) (ทั้งนี้ ความสามารถนี้เริ่มเปิดตัวในช่วงกลางปี 2025 หากคุณกำลังอ่านข้อความนี้อยู่ เราอาจจะกำลังทยอยปรับปรุงความเสถียรอยู่)

คุณสามารถใช้งานฟีเจอร์นี้ได้ผ่านการผสาน 3 ส่วนประกอบเข้าด้วยกัน: แฟล็ก `cargo leptos (serve|watch|build) --split`, มาโคร [`#[lazy]`](https://docs.rs/leptos/latest/leptos/attr.lazy.html) และมาโคร [`#[lazy_route]`](https://docs.rs/leptos_router/latest/leptos_router/attr.lazy_route.html) (ควบคู่กับเทรต [`LazyRoute`](https://docs.rs/leptos_router/latest/leptos_router/trait.LazyRoute.html))

### `#[lazy]`

มาโคร `#[lazy]` ใช้ระบุว่าฟังก์ชันดังกล่าวสามารถโหลดแบบ lazy (lazy-loaded) มาจากไฟล์ไบนารี WASM แยกต่างหากได้ สามารถใช้แอนโนเทตได้ทั้งฟังก์ชันแบบ synchronous หรือ async ซึ่งทั้งสองกรณีจะให้ผลลัพธ์เป็นฟังก์ชันแบบ async โดยในการเรียกใช้ฟังก์ชันแบบ lazy ครั้งแรก โค้ดส่วนย่อยนั้นจะถูกดาวน์โหลดจากเซิร์ฟเวอร์และเริ่มทำงาน จากนั้นในการเรียกครั้งถัด ๆ ไป ฟังก์ชันจะทำงานได้ทันทีโดยไม่ต้องผ่านขั้นตอนดาวน์โหลดซ้ำอีก

```rust
#[lazy]
fn lazy_synchronous_function() -> String {
    "Hello, lazy world!".to_string()
}

#[lazy]
async fn lazy_async_function() -> String {
    /* do something that requires async work */
    "Hello, lazy async world!".to_string()
}

async fn use_lazy_functions() {
    // synchronous function has been converted to async
    let value1 = lazy_synchronous_function().await;

    // async function is still async
    let value1 = lazy_async_function().await;
}
```

วิธีนี้มีประโยชน์สำหรับการทำ lazy function ทั่วไป แต่การโหลดแบบ lazy จะทรงพลังที่สุดเมื่อทำงานร่วมกับเราเตอร์

### `#[lazy_route]`

Lazy route ช่วยให้คุณสามารถแยกโค้ดส่วน view ของแต่ละ route ออกมา และโหลดแบบ lazy ไปพร้อม ๆ กับการโหลดข้อมูลของเส้นทางนั้นขณะที่ผู้ใช้นำทาง ด้วยการใช้ nested routing คุณสามารถซ้อน lazy route ได้หลายชั้น โดยแต่ละเส้นทางจะโหลดข้อมูลและ view ของตนเองไปพร้อม ๆ กันแบบ concurrent

การแยกการโหลดข้อมูลออกจากตัว view (ที่โหลดแบบ lazy) ช่วยป้องกันปัญหาคอขวดแบบ “waterfall” ซึ่งเกิดจากการต้องรอให้ไฟล์ view โหลดเสร็จสิ้นก่อน แล้วจึงค่อยเริ่มส่งคำขอข้อมูล

```rust
use leptos::prelude::*;
use leptos_router::{lazy_route, LazyRoute};

// the route definition
#[derive(Debug)]
struct BlogListingRoute {
    titles: Resource<Vec<String>>
}

#[lazy_route]
impl LazyRoute for BlogListingRoute {
    fn data() -> Self {
        Self {
            titles: Resource::new(|| (), |_| async {
                vec![/* todo: load blog posts */]
            })
        }
    }

    // this function will be lazy-loaded, concurrently with data()
    fn view(this: Self) -> AnyView {
        let BlogListingRoute { titles } = this;

        // ... now you can use the `posts` resource with Suspense, etc.,
        // and return AnyView by calling .into_any() on a view
    }
}
```

### ตัวอย่างและข้อมูลเพิ่มเติม

คุณสามารถศึกษาการอธิบายเชิงลึกเพิ่มเติมได้จาก [วิดีโอบน YouTube นี้](https://www.youtube.com/watch?v=w5fhcoxQnII) และดูตัวอย่างโค้ดฉบับเต็มของ [`lazy_routes`](https://github.com/leptos-rs/leptos/blob/main/examples/lazy_routes/src/app.rs) ได้ในคลังตัวอย่างของ Leptos
